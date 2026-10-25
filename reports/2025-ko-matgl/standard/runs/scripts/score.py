"""Score the COMP6 predictions against the pre-registered claims (claims.json).

Usage: python score.py <npz_dir> <claims.json> <out_prefix>
Writes <out_prefix>.json (everything) and <out_prefix>.md (tables).
"""
import json
import os
import sys

import numpy as np

GROUPS = {
    "ANI-MD": ["ani_md_bench"],
    "GDB 9-11": ["gdb11_07_test500", "gdb11_08_test500", "gdb11_09_test500"],
    "GDB 12-13": ["gdb11_10_test500", "gdb11_11_test500", "gdb13_12_test1000", "gdb13_13_test1000"],
    "Drugbank": ["drugbank_testset"],
    "S66x8": ["s66x8_wb97x6-31gd"],
    "Tripeptides": ["tripeptide_full"],
}
ALT_GDB_GROUPS = {
    "GDB 9-11": ["gdb11_09_test500", "gdb11_10_test500", "gdb11_11_test500"],
    "GDB 12-13": ["gdb13_12_test1000", "gdb13_13_test1000"],
}
MODELS = ["M3GNet", "TensorNet", "SO3Net"]


def per_file_stats(npz_path):
    data = np.load(npz_path)
    n_atoms = data["n_atoms"].astype(np.float64)
    energy_abs_err = np.abs(data["energy_pred_eV"] - data["energy_ref_eV"])
    force_diff = data["forces_pred_eV_per_A"].astype(np.float64) - data["forces_ref_eV_per_A"].astype(np.float64)
    force_abs = np.abs(force_diff)
    atom_offsets = np.concatenate([[0], np.cumsum(data["n_atoms"])])
    per_conf_force_component_mae = np.add.reduceat(force_abs.sum(axis=1), atom_offsets[:-1]) / (3 * n_atoms)
    # Exploratory, not pre-registered: remove each molecule's mean energy error (conformer energies relative to the molecule)
    signed_err = data["energy_pred_eV"] - data["energy_ref_eV"]
    molecule_index = data["molecule_index"]
    molecule_mean_err = np.zeros(molecule_index.max() + 1)
    np.add.at(molecule_mean_err, molecule_index, signed_err)
    molecule_mean_err /= np.maximum(np.bincount(molecule_index), 1)
    centered_abs_err = np.abs(signed_err - molecule_mean_err[molecule_index])
    return {
        "energy_abs_err": energy_abs_err,
        "energy_centered_abs_err": centered_abs_err,
        "energy_signed_err": signed_err,
        "n_atoms": n_atoms,
        "force_abs_sum": float(force_abs.sum()),
        "force_component_count": int(force_abs.size),
        "force_norm_sum": float(np.linalg.norm(force_diff, axis=1).sum()),
        "atom_count": int(force_diff.shape[0]),
        "per_conf_force_component_mae": per_conf_force_component_mae,
        "excluded": int(len(data["excluded"])),
    }


def group_metrics(stats_list):
    energy_abs_err = np.concatenate([s["energy_abs_err"] for s in stats_list])
    n_atoms = np.concatenate([s["n_atoms"] for s in stats_list])
    force_abs_sum = sum(s["force_abs_sum"] for s in stats_list)
    force_count = sum(s["force_component_count"] for s in stats_list)
    per_conf_force = np.concatenate([s["per_conf_force_component_mae"] for s in stats_list])
    return {
        "n_conformations": int(len(energy_abs_err)),
        "n_atoms_total": int(n_atoms.sum()),
        "excluded": sum(s["excluded"] for s in stats_list),
        # Primary D-EMAE: mean over conformations of |dE|/N
        "energy_mae_meV_per_atom": float(np.mean(energy_abs_err / n_atoms) * 1000),
        # Primary D-FMAE: pooled over every force component
        "force_mae_eV_per_A": force_abs_sum / force_count,
        # Alternatives (secondary)
        "alt_b_energy_total_mae_over_mean_n": float(np.mean(energy_abs_err) / np.mean(n_atoms) * 1000),
        "alt_c_energy_sum_dE_over_sum_n": float(energy_abs_err.sum() / n_atoms.sum() * 1000),
        "alt_d_energy_unweighted_file_mean": float(np.mean([np.mean(s["energy_abs_err"] / s["n_atoms"]) * 1000 for s in stats_list])),
        "alt_b_force_mean_of_per_conf_mae": float(per_conf_force.mean()),
        "alt_c_force_vector_norm_per_atom": sum(s["force_norm_sum"] for s in stats_list) / sum(s["atom_count"] for s in stats_list),
        "alt_d_force_unweighted_file_mean": float(np.mean([s["force_abs_sum"] / s["force_component_count"] for s in stats_list])),
        "total_energy_mae_meV": float(np.mean(energy_abs_err) * 1000),
        "mean_signed_energy_err_meV_per_atom": float(np.mean(np.concatenate([s["energy_signed_err"] for s in stats_list]) / n_atoms) * 1000),
        "exploratory_molecule_centered_energy_mae_meV_per_atom": float(np.mean(np.concatenate([s["energy_centered_abs_err"] for s in stats_list]) / n_atoms) * 1000),
        "mean_atoms_per_conformation": float(n_atoms.mean()),
    }


def grade(ours, claim):
    tolerance = claim["tolerance"]["absolute"]
    difference = abs(ours - claim["paper_value"])
    if difference <= tolerance:
        return "match"
    if difference <= 3 * tolerance:
        return "close"
    return "mismatch"


def text_check(claim, ours):
    rule = claim.get("text_check_secondary")
    if not rule:
        return None
    checks = {
        "E-M3GNet-ANIMD": ours > 14.0,
        "F-M3GNet-ANIMD": ours > 0.14,
        "E-TensorNet-ANIMD": 10.5 <= ours < 11.5,
        "F-TensorNet-ANIMD": 0.05 <= ours < 0.15,
        "E-SO3Net-ANIMD": 2.25 <= ours < 2.35,
        "F-SO3Net-ANIMD": 0.0435 <= ours < 0.0445,
    }
    return {"rule": rule, "pass": bool(checks[claim["id"]])}


def main(npz_dir, claims_path, out_prefix):
    claims = json.load(open(claims_path, encoding="utf-8"))
    stats = {}
    for model in MODELS:
        for files in GROUPS.values():
            for stem in files:
                stats[(model, stem)] = per_file_stats(os.path.join(npz_dir, f"{model}__{stem}.npz"))

    results = {"primary": {}, "per_file": {}, "alt_gdb_grouping": {}}
    for model in MODELS:
        for group, files in GROUPS.items():
            results["primary"][f"{model}|{group}"] = group_metrics([stats[(model, s)] for s in files])
        for files in GROUPS.values():
            for stem in files:
                results["per_file"][f"{model}|{stem}"] = group_metrics([stats[(model, stem)]])
        for group, files in ALT_GDB_GROUPS.items():
            results["alt_gdb_grouping"][f"{model}|{group}"] = group_metrics([stats[(model, s)] for s in files])

    claim_rows = []
    for claim in claims["claims"]:
        metrics = results["primary"][f"{claim['model']}|{claim['group_label_in_figure']}"]
        is_energy = claim["id"].startswith("E-")
        ours = metrics["energy_mae_meV_per_atom" if is_energy else "force_mae_eV_per_A"]
        row = {
            "id": claim["id"], "model": claim["model"], "group": claim["group_label_in_figure"],
            "quantity": "energy" if is_energy else "force", "paper": claim["paper_value"], "ours": ours,
            "diff": ours - claim["paper_value"], "rel_diff": (ours - claim["paper_value"]) / claim["paper_value"],
            "tolerance": claim["tolerance"]["absolute"], "grade": grade(ours, claim),
            "text_check": text_check(claim, ours),
        }
        claim_rows.append(row)
    results["claims"] = claim_rows

    n_match = sum(r["grade"] == "match" for r in claim_rows)
    n_close = sum(r["grade"] == "close" for r in claim_rows)
    n_mismatch = sum(r["grade"] == "mismatch" for r in claim_rows)
    if n_match == 36:
        verdict = "Reproduced"
    elif n_match >= 18 or n_match + n_close == 36:
        verdict = "Partially reproduced"
    else:
        verdict = "Not reproduced"
    results["summary"] = {"match": n_match, "close": n_close, "mismatch": n_mismatch, "verdict": verdict}

    with open(out_prefix + ".json", "w") as handle:
        json.dump(results, handle, indent=1)

    lines = ["| Claim | Paper | Ours | Diff | Rel | Tol | Grade |", "|---|---|---|---|---|---|---|"]
    for r in claim_rows:
        digits = 3 if r["quantity"] == "energy" else 4
        lines.append(f"| {r['id']} | {r['paper']} | {r['ours']:.{digits}f} | {r['diff']:+.{digits}f} | "
                     f"{100 * r['rel_diff']:+.1f}% | {r['tolerance']:.{digits}f} | {r['grade']} |")
    lines.append("")
    lines.append(f"match {n_match}, close {n_close}, mismatch {n_mismatch}: {verdict}")
    with open(out_prefix + ".md", "w") as handle:
        handle.write("\n".join(lines) + "\n")
    print("\n".join(lines))


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2], sys.argv[3])
