"""Aggregate the per-config CSVs into the pre-registered claims and check the bands."""
import csv
import json
import os
import sys

import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODEL_KEY = {"MACE-OFF23(S)": "small", "MACE-OFF23(M)": "medium", "MACE-OFF23(L)": "large"}
SUBSET_KEY = {
    "PubChem": "PubChem",
    "DES370K Monomers": "DES370K Monomers",
    "DES370K Dimers": "DES370K Dimers",
    "Dipeptides": "Dipeptides",
    "Solvated Amino Acids": "Solvated Amino Acids",
    "water": "water",
    "QMugs": "QMugs",
}
EV_TO_MEV = 1000.0


def load(path):
    rows = {}
    with open(path, newline="") as fh:
        for r in csv.DictReader(fh):
            rows.setdefault(r["config_type"], []).append((
                int(r["n_atoms"]),
                float(r["abs_e_err_per_atom_eV"]),
                float(r["sum_abs_f_comp_err_eV_A"]),
                float(r["sum_abs_f_vec_err_eV_A"]),
                float(r["ref_max_abs_f_eV_A"]),
                float(r["ref_sum_f_norm_eV_A"]),
            ))
    return {k: np.array(v) for k, v in rows.items()}


def agg(a, keep=None):
    """Return (n, energy MAE meV/atom, force component MAE meV/A, force vector MAE meV/A)."""
    if keep is not None:
        a = a[keep]
    nat = a[:, 0]
    e = a[:, 1].mean() * EV_TO_MEV
    f_comp = a[:, 2].sum() / (3.0 * nat.sum()) * EV_TO_MEV
    f_vec = a[:, 3].sum() / nat.sum() * EV_TO_MEV
    return len(a), e, f_comp, f_vec


def band(paper, kind, metric):
    rel = 0.15 if kind == "wide" else 0.05
    floor = 0.02 if metric == "energy_mae" else 0.2
    return max(rel * paper, floor)


def main():
    claims = json.load(open(os.path.join(ROOT, "claims.json")))
    per_model = {}
    for key in ("small", "medium", "large"):
        p = os.path.join(ROOT, "runs", "out", f"errors_{key}.csv")
        if not os.path.exists(p):
            print(f"missing {p}", file=sys.stderr)
            sys.exit(1)
        per_model[key] = load(p)

    out = []
    inside = 0
    worst = 0.0
    for c in claims["claims"]:
        a = per_model[MODEL_KEY[c["model"]]][SUBSET_KEY[c["subset"]]]
        n, e, f_comp, _ = agg(a)
        ours = e if c["metric"] == "energy_mae" else f_comp
        tol = band(c["paper"], c["band"], c["metric"])
        d = abs(ours - c["paper"])
        ok = d <= tol
        inside += ok
        worst = max(worst, d / c["paper"])
        out.append({
            "id": c["id"], "model": c["model"], "metric": c["metric"], "subset": c["subset"],
            "n": int(n), "paper": c["paper"], "ours": round(float(ours), 4), "unit": c["unit"],
            "band": c["band"], "tol": round(float(tol), 4),
            "diff": round(float(ours - c["paper"]), 4),
            "rel_pct": round(100.0 * float(ours - c["paper"]) / c["paper"], 2),
            "result": "inside" if ok else "outside",
        })

    print(f"{'claim':34s} {'paper':>8s} {'ours':>9s} {'tol':>7s} {'rel%':>8s}  result")
    for r in out:
        print(f"{r['id']:34s} {r['paper']:8.2f} {r['ours']:9.3f} {r['tol']:7.3f} {r['rel_pct']:8.2f}  {r['result']}")
    print(f"\ninside: {inside}/42   worst relative deviation: {100 * worst:.1f}%")
    rule = claims["verdict_rule"]
    if inside >= 38 and worst <= 0.25:
        verdict = "Reproduced"
    elif inside >= 26:
        verdict = "Partially reproduced"
    else:
        verdict = "Not reproduced"
    print("verdict by the pre-registered rule:", verdict)
    print(" rule:", json.dumps(rule))

    # Alternative readings, declared in claims.json before the run.
    print("\n--- A1: force MAE as mean per-atom vector norm (meV/A)")
    for key in ("small", "medium", "large"):
        for s in SUBSET_KEY:
            n, e, fc, fv = agg(per_model[key][s])
            print(f"  {key:6s} {s:22s} n={n:6d}  comp={fc:8.3f}  vecnorm={fv:8.3f}")

    print("\n--- A2: PubChem and DES370K Dimers after the SPICE v2 force filters")
    for key in ("small", "medium", "large"):
        for s in ("PubChem", "DES370K Dimers"):
            a = per_model[key][s]
            keep = (a[:, 4] <= 15.0) & (a[:, 5] <= 0.1)
            n0, e0, fc0, _ = agg(a)
            n1, e1, fc1, _ = agg(a, keep)
            print(f"  {key:6s} {s:16s} all n={n0:6d} E={e0:7.3f} F={fc0:8.3f} | "
                  f"filtered n={n1:6d} E={e1:7.3f} F={fc1:8.3f} (dropped {n0 - n1})")

    with open(os.path.join(ROOT, "runs", "out", "claims_result.json"), "w") as fh:
        json.dump({"verdict": verdict, "inside": int(inside), "total": 42,
                   "worst_rel": float(worst), "claims": out}, fh, indent=1)
    with open(os.path.join(ROOT, "runs", "out", "claims_result.csv"), "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(out[0].keys()))
        w.writeheader()
        w.writerows(out)


if __name__ == "__main__":
    main()
