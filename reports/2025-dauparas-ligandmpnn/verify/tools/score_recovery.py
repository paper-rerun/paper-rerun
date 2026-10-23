"""Native sequence recovery near the ligand, written from the paper's definitions.

Two readings of "near" are scored side by side, because the paper states two:
  any_atom   - Fig. 2a legend, "residues within 5.0 A from the context atoms"
  sidechain  - Results, "sidechain atoms within 5.0 A of any nonprotein atoms"
               (N, CA, C, O, OXT excluded, so glycine never qualifies)
Testing both against the authors' own per-protein denominators in Source Data
Fig. 2 showed any_atom is what they computed, so that is the primary.

Two readings of "the context" are scored as well:
  all               - every non-protein, non-water heavy atom
  metal_transition  - only transition-metal atoms
The second exists because the metal split's published denominators are far too
small for the first: 1dwh solves to 3 scored residues where every hetero atom in
the file gives 122, and 3 is what one calcium site gives.

Aggregation follows the Fig. 2a legend: mean over the 10 designed sequences per
protein, then the median of those across the split.

None of the authors' scoring code is used. The only thing taken from their side
is the designed sequence itself, read out of the .pt that run.py writes under
--save_stats 1, which is in the residue order their own parser produces. That
order is rebuilt here independently and checked length against length.
"""

import json
import os
import sys

import numpy as np
import torch
from prody import confProDy, parsePDB
from scipy.spatial import cKDTree

confProDy(verbosity="critical")

BACKBONE = {"N", "CA", "C", "O", "OXT"}
CUTOFF = 5.0
TRANSITION = set("SC TI V CR MN FE CO NI CU ZN Y ZR NB MO TC RU RH PD AG CD "
                 "HF TA W RE OS IR PT AU HG".split())
COMBOS = [("any_atom", "all"), ("sidechain", "all"), ("any_atom", "metal_transition")]


def parse(path):
    atoms = parsePDB(path)
    if atoms is None:
        raise RuntimeError("prody could not parse %s" % path)
    atoms = atoms.select("occupancy > 0")
    protein = atoms.select("protein")
    other = atoms.select("not protein and not water")
    if protein is None:
        raise RuntimeError("no protein atoms in %s" % path)
    return atoms, protein, other


def masks_for(path):
    """One boolean mask per (mode, context) combo, in CA order, plus a few counts."""
    atoms, protein, other = parse(path)
    ca = protein.select("name CA")
    keys = list(zip(ca.getChids(), ca.getResnums(), [str(i) for i in ca.getIcodes()]))
    index = {}
    n_dup = 0
    for i, k in enumerate(keys):
        if k in index:
            n_dup += 1
        else:
            index[k] = i
    n_res = len(keys)
    info = {"n_residues": n_res, "n_duplicate_ca_keys": n_dup}

    # context atom sets
    ctx = {"all": np.zeros((0, 3)), "metal_transition": np.zeros((0, 3))}
    if other is not None:
        el = np.array([str(e).strip().upper() for e in other.getElements()])
        xyz = np.asarray(other.getCoords(), float)
        heavy = ~np.isin(el, ["H", "D"])
        ctx["all"] = xyz[heavy]
        ctx["metal_transition"] = xyz[heavy & np.isin(el, list(TRANSITION))]
    info["n_context_all"] = int(len(ctx["all"]))
    info["n_context_metal"] = int(len(ctx["metal_transition"]))

    # protein atom sets
    p_names = np.array([str(n).strip() for n in protein.getNames()])
    p_el = np.array([str(e).strip().upper() for e in protein.getElements()])
    p_keys = list(zip(protein.getChids(), protein.getResnums(),
                      [str(i) for i in protein.getIcodes()]))
    p_xyz = np.asarray(protein.getCoords(), float)
    heavy = ~np.isin(p_el, ["H", "D"])
    sets = {
        "any_atom": heavy,
        "sidechain": heavy & ~np.isin(p_names, list(BACKBONE)),
    }

    out = {}
    for mode, context in COMBOS:
        sel = sets[mode]
        cx = ctx[context]
        mask = np.zeros(n_res, bool)
        if len(cx) and sel.any():
            tree = cKDTree(cx)
            sub_xyz = p_xyz[sel]
            sub_keys = [k for k, s in zip(p_keys, sel) if s]
            for a, h in enumerate(tree.query_ball_point(sub_xyz, r=CUTOFF)):
                if h:
                    j = index.get(sub_keys[a])
                    if j is not None:
                        mask[j] = True
        out["%s|%s" % (mode, context)] = mask
    return out, info


def score_one(stats_path, structure_path):
    d = torch.load(stats_path, map_location="cpu")
    gen = d["generated_sequences"].numpy()
    native = d["native_sequence"].numpy()
    valid = d["mask"].numpy().astype(bool)
    chain = d["chain_mask"].numpy().astype(bool)

    masks, info = masks_for(structure_path)
    for key, mask in masks.items():
        if len(mask) != len(native):
            raise RuntimeError("length mismatch %s: parser %d vs stats %d"
                               % (structure_path, len(mask), len(native)))

        def rec_over(sel):
            if not sel.sum():
                return None, []
            v = (gen[:, sel] == native[None, sel]).mean(axis=1) * 100.0
            return float(v.mean()), [round(float(x), 6) for x in v]

        rec, per_seq = rec_over(mask)
        rec_gated, _ = rec_over(mask & valid & chain)
        info[key] = {
            "n_scored": int(mask.sum()),
            "n_dropped_by_valid_or_chain": int((mask & ~(valid & chain)).sum()),
            "recovery": rec,
            "recovery_backbone_complete_only": rec_gated,
            "per_sequence": per_seq,
        }
    info["n_sequences"] = int(gen.shape[0])
    info["seed"] = int(d.get("seed", -1))
    info["temperature"] = float(d.get("temperature", -1))
    return info


def main():
    split = sys.argv[1]
    model = sys.argv[2]
    # Optional: take the designed sequences from a different run. ProteinMPNN never
    # sees context atoms, so its designs are identical whatever context the input
    # file carries; only the scored set changes. That lets the class-only reading
    # be evaluated for ProteinMPNN by re-scoring, with no second GPU run.
    stats_split = sys.argv[3] if len(sys.argv) > 3 else split
    vroot = "/mnt/e/Ciencia/pipeline/2025-dauparas-ligandmpnn/verify"
    index = json.load(open(vroot + "/inputs/index.json"))[split]
    stats_dir = "%s/out/%s_%s/stats" % (vroot, model, stats_split)

    rows = []
    for n, entry in enumerate(index, 1):
        sp = os.path.join(stats_dir, entry["name"] + ".pt")
        if not os.path.exists(sp):
            rows.append({"name": entry["name"], "error": "no stats file"})
            continue
        try:
            info = score_one(sp, entry["path"])
            info["name"] = entry["name"]
        except Exception as err:
            info = {"name": entry["name"], "error": "%s: %s" % (type(err).__name__, err)}
        rows.append(info)
        if n % 50 == 0:
            print("...", n, "of", len(index), flush=True)

    out = {"split": split, "model": model, "n_total": len(rows)}
    for mode, context in COMBOS:
        key = "%s|%s" % (mode, context)
        vals = [r[key]["recovery"] for r in rows
                if key in r and r[key]["recovery"] is not None]
        out[key] = {
            "n_proteins": len(vals),
            "n_missing": len(rows) - len(vals),
            "median_recovery": float(np.median(vals)) if vals else None,
            "mean_recovery": float(np.mean(vals)) if vals else None,
        }
    out["errors"] = [r for r in rows if "error" in r]
    out["per_protein"] = rows

    # Name the output after the run the sequences came from, not just the input
    # index, or re-scoring a variant run overwrites the claim run's result.
    tag = split if stats_split == split else "%s_from_%s" % (split, stats_split)
    dest = "%s/out/score_%s_%s.json" % (vroot, model, tag)
    with open(dest, "w") as fh:
        json.dump(out, fh, indent=1)
    print(json.dumps({k: v for k, v in out.items()
                      if k not in ("per_protein", "errors")}, indent=1))
    print("errors:", len(out["errors"]))
    print("wrote", dest)


if __name__ == "__main__":
    sys.exit(main())
