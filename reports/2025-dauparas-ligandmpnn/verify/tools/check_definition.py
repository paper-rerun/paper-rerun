"""Settle two things from published data alone, before any of our numbers exist.

1. Which residues are scored. The Results says "sidechain atoms within 5.0 A of
   any nonprotein atoms"; the Fig. 2a legend says "residues within 5.0 A from the
   context atoms". Those are different sets, so test both.
2. For the nucleotide and metal splits, whether the input was the asymmetric unit
   or biological assembly 1.

The test: each per-protein value in Source Data Fig. 2 is a mean over 10
sequences of count/n, hence an exact multiple of 100/(10n). Compute n for a
candidate, then check whether the authors' two recovery columns both land on
such a multiple. A wrong candidate fails nearly everywhere.
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
BACKBONE = {"N", "CA", "C", "O", "OXT"}
CUTOFF = 5.0


def count_near(path, mode):
    atoms = parsePDB(path)
    if atoms is None:
        return None, None
    atoms = atoms.select("occupancy > 0")
    protein = atoms.select("protein")
    other = atoms.select("not protein and not water")
    if protein is None:
        return None, None
    ca = protein.select("name CA")
    if ca is None:
        return None, None
    keys = list(zip(ca.getChids(), ca.getResnums(), [str(i) for i in ca.getIcodes()]))
    index = {}
    for i, k in enumerate(keys):
        index.setdefault(k, i)
    if other is None:
        return 0, len(keys)

    o_el = np.array([str(e).strip().upper() for e in other.getElements()])
    o_xyz = np.asarray(other.getCoords(), float)[~np.isin(o_el, ["H", "D"])]
    if len(o_xyz) == 0:
        return 0, len(keys)

    names = [str(n).strip() for n in protein.getNames()]
    els = [str(e).strip().upper() for e in protein.getElements()]
    pkeys = list(zip(protein.getChids(), protein.getResnums(),
                     [str(i) for i in protein.getIcodes()]))
    coords = np.asarray(protein.getCoords(), float)

    sel_xyz, sel_res = [], []
    for i, k in enumerate(pkeys):
        if els[i] in ("H", "D"):
            continue
        if mode == "sidechain" and names[i] in BACKBONE:
            continue
        j = index.get(k)
        if j is None:
            continue
        sel_xyz.append(coords[i])
        sel_res.append(j)

    mask = np.zeros(len(keys), bool)
    if sel_xyz:
        tree = cKDTree(o_xyz)
        for n, h in enumerate(tree.query_ball_point(np.asarray(sel_xyz), r=CUTOFF)):
            if h:
                mask[sel_res[n]] = True
    return int(mask.sum()), len(keys)


def integer_ok(value, n, tol=2e-3):
    if not n:
        return False
    total = value * 10.0 * n / 100.0
    return abs(total - round(total)) < tol


SPLITS = [
    ("small_molecule", "fig_2_1", "test_small_molecule.json"),
    ("nucleotide", "fig_2_2", "test_nucleotide.json"),
    ("metal", "fig_2_3", "test_metal.json"),
]


def candidates(split, name, pdb_id):
    """(label, path) inputs to try for one protein."""
    if split == "small_molecule":
        return [("chain+ligand", ROOT + "/verify/inputs/small_molecule/" + name + ".pdb")]
    return [("asym", ROOT + "/data/structures/asym/" + pdb_id + ".pdb"),
            ("biounit1", ROOT + "/data/structures/biounit1/" + pdb_id + ".pdb")]


def main():
    summary = {}
    for split, stem, listname in SPLITS:
        d = np.load(SD + "/" + stem + "_2.npz", allow_pickle=True)
        p1x, p1y = d["p1x"].astype(float), d["p1y"].astype(float)
        names = [str(x)[:-4] for x in d["names"]]
        ids = json.load(open(ROOT + "/repo/training/" + listname))

        tally = {}
        rows = []
        for i, nm in enumerate(names):
            row = {"name": nm, "p1x": p1x[i], "p1y": p1y[i]}
            for label, path in candidates(split, nm, ids[i]):
                for mode in ("any_atom", "sidechain"):
                    key = "%s/%s" % (label, mode)
                    n, total = count_near(path, mode)
                    good = integer_ok(p1x[i], n) and integer_ok(p1y[i], n)
                    t = tally.setdefault(key, [0, 0])
                    t[0] += int(good)
                    t[1] += 1
                    row[key] = [n, total, bool(good)]
            rows.append(row)
            if (i + 1) % 50 == 0:
                print("  ...", split, i + 1, "/", len(names), flush=True)

        print("\n=== %s (n=%d) ===" % (split, len(names)))
        for key, (hit, tot) in sorted(tally.items(), key=lambda kv: -kv[1][0]):
            print("   %-24s %3d / %3d  (%.0f%%)" % (key, hit, tot, 100.0 * hit / tot))
        summary[split] = {"tally": {k: v for k, v in tally.items()}, "rows": rows}

    with open(ROOT + "/verify/out/definition_check.json", "w") as fh:
        json.dump(summary, fh, indent=1, default=float)
    print("\nwrote verify/out/definition_check.json")


if __name__ == "__main__":
    sys.exit(main())
