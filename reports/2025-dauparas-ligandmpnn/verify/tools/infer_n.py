"""Which residues did the authors actually score?

Every per-protein value in Source Data Fig. 2 is a mean over 10 sequences of
count/n, so it is an exact multiple of 100/(10n). That makes n testable: pick a
candidate definition of "near the ligand", compute n for each protein, and check
whether the authors' own two recovery columns land on multiples of 100/(10n).
The right definition should pass on essentially all 317 proteins; a wrong one
fails almost everywhere.

This fixes the definition from published numbers only. It never looks at a
recovery value we produced - nothing of ours exists yet when this runs.
"""

import json
import os
import sys

import numpy as np
from prody import confProDy, parsePDB
from scipy.spatial import cKDTree

confProDy(verbosity="critical")

ROOT = "/mnt/e/Ciencia/pipeline/2025-dauparas-ligandmpnn"
SD = ROOT + "/sources/sd/x/s2"
ASYM = ROOT + "/data/structures/asym"
BACKBONE = {"N", "CA", "C", "O", "OXT"}
CUTOFF = 5.0


def residue_table(path):
    atoms = parsePDB(path).select("occupancy > 0")
    protein = atoms.select("protein")
    other = atoms.select("not protein and not water")
    ca = protein.select("name CA")
    keys = list(zip(ca.getChids(), ca.getResnums(), [str(i) for i in ca.getIcodes()]))
    index = {}
    for i, k in enumerate(keys):
        index.setdefault(k, i)
    return atoms, protein, other, keys, index


def count_near(path, mode, context_path=None):
    """n for one candidate definition."""
    atoms, protein, other, keys, index = residue_table(path)
    if context_path:  # context taken from the whole deposited entry instead
        c_atoms = parsePDB(context_path).select("occupancy > 0")
        other = c_atoms.select("not protein and not water")
    if other is None:
        return 0, len(keys)

    o_el = np.array([str(e).strip().upper() for e in other.getElements()])
    o_xyz = np.asarray(other.getCoords(), float)
    if mode != "ctx_with_H":
        o_xyz = o_xyz[~np.isin(o_el, ["H", "D"])]
    if len(o_xyz) == 0:
        return 0, len(keys)

    names = [str(n).strip() for n in protein.getNames()]
    els = [str(e).strip().upper() for e in protein.getElements()]
    pkeys = list(zip(protein.getChids(), protein.getResnums(),
                     [str(i) for i in protein.getIcodes()]))
    coords = np.asarray(protein.getCoords(), float)
    resnames = np.array(protein.getResnames())

    sel_xyz, sel_res = [], []
    for i, k in enumerate(pkeys):
        j = index.get(k)
        if j is None:
            continue
        if els[i] in ("H", "D") and mode != "protein_with_H":
            continue
        if mode in ("any_atom", "ctx_with_H", "protein_with_H"):
            pass                                   # every atom of the residue
        elif mode == "sidechain_plus_CA":
            if names[i] in (BACKBONE - {"CA"}):
                continue
        elif mode == "sidechain_keep_OXT":
            if names[i] in (BACKBONE - {"OXT"}):
                continue
        else:                                      # "sidechain" (the literal reading)
            if names[i] in BACKBONE:
                continue
        sel_xyz.append(coords[i])
        sel_res.append(j)

    mask = np.zeros(len(keys), bool)
    if sel_xyz:
        tree = cKDTree(o_xyz)
        for n, h in enumerate(tree.query_ball_point(np.asarray(sel_xyz), r=CUTOFF)):
            if h:
                mask[sel_res[n]] = True

    if mode == "sidechain_plus_virtualCB":
        pass
    return int(mask.sum()), len(keys)


def integer_ok(value, n, n_seq=10, tol=2e-3):
    """Is `value` a mean over n_seq sequences of count/n, in percent?"""
    if n == 0:
        return False
    total = value * n_seq * n / 100.0
    return abs(total - round(total)) < tol


def main():
    names = json.load(open(ROOT + "/sources/fig2b_names.json"))["small_molecule"]
    d = np.load(SD + "/fig_2_1_2.npz", allow_pickle=True)
    p1x = d["p1x"].astype(np.float64)
    p1y = d["p1y"].astype(np.float64)
    p1c = d["p1c"].astype(np.float64)
    print("medians  p1x=%.3f  p1y=%.3f  p1c=%.3f"
          % (np.median(p1x), np.median(p1y), np.median(p1c)))
    print("paper    Rosetta=50.435  ProteinMPNN=50.476  LigandMPNN=63.333")

    modes = ["sidechain", "any_atom", "sidechain_plus_CA", "sidechain_keep_OXT",
             "ctx_with_H", "protein_with_H"]
    limit = int(sys.argv[1]) if len(sys.argv) > 1 else 60

    results = {m: [0, 0] for m in modes}
    results["sidechain_ctx_whole_entry"] = [0, 0]
    detail = []

    for i, nm in enumerate(names[:limit]):
        stem = nm[:-4]
        path = ROOT + "/verify/inputs/small_molecule/" + stem + ".pdb"
        whole = os.path.join(ASYM, stem[:4] + ".pdb")
        row = {"name": stem, "p1x": p1x[i], "p1y": p1y[i]}
        for m in modes:
            n, _ = count_near(path, m)
            good = integer_ok(p1x[i], n) and integer_ok(p1y[i], n)
            results[m][0] += int(good)
            results[m][1] += 1
            row[m] = (n, good)
        n, _ = count_near(path, "sidechain", context_path=whole)
        good = integer_ok(p1x[i], n) and integer_ok(p1y[i], n)
        results["sidechain_ctx_whole_entry"][0] += int(good)
        results["sidechain_ctx_whole_entry"][1] += 1
        row["sidechain_ctx_whole_entry"] = (n, good)
        detail.append(row)
        if (i + 1) % 20 == 0:
            print("...", i + 1, flush=True)

    print("\n%-32s %s" % ("definition", "proteins whose n explains BOTH authors' columns"))
    for m, (hit, tot) in sorted(results.items(), key=lambda kv: -kv[1][0]):
        print("%-32s %3d / %3d" % (m, hit, tot))

    print("\nfirst 12 proteins, n per definition:")
    hdr = ["name", "p1x", "p1y"] + modes + ["sidechain_ctx_whole_entry"]
    print(" | ".join(h[:14] for h in hdr))
    for row in detail[:12]:
        cells = [row["name"], "%.4f" % row["p1x"], "%.4f" % row["p1y"]]
        for m in modes + ["sidechain_ctx_whole_entry"]:
            n, good = row[m]
            cells.append("%d%s" % (n, "*" if good else ""))
        print(" | ".join(c[:14] for c in cells))

    with open(ROOT + "/verify/out/infer_n.json", "w") as fh:
        json.dump({"counts": results,
                   "detail": [{k: (list(v) if isinstance(v, tuple) else v)
                               for k, v in r.items()} for r in detail]}, fh, indent=1, default=float)


if __name__ == "__main__":
    os.makedirs(ROOT + "/verify/out", exist_ok=True)
    sys.exit(main())
