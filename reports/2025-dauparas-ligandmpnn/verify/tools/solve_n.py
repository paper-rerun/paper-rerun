"""Recover, protein by protein, how many residues the authors actually scored.

Each Source Data value is a mean over 10 sequences of count/n, so value*n/10 must
be a whole number. Three methods are published per protein (Rosetta, ProteinMPNN,
LigandMPNN), which is three independent constraints on the same n - sharp enough
that usually one small n survives.

Then compare that n against what each candidate input produces, to settle whether
the nucleotide and metal splits used the asymmetric unit or biological assembly 1,
and which residues count as "near".
"""

import collections
import csv
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
METHODS = ["Rosetta", "ProteinMPNN", "LigandMPNN"]
STEM = {"small_molecule": "fig_2_1", "nucleotide": "fig_2_2", "metal": "fig_2_3"}
FIXED_5L70 = {"asym": ROOT + "/verify/inputs/fixed/5l70_asym.pdb",
              "biounit1": ROOT + "/verify/inputs/fixed/5l70_biounit1.pdb"}


def load_values(split):
    rows = list(csv.DictReader(open(os.path.join(SD, STEM[split] + "_1.csv"))))
    out = {}
    for m in METHODS:
        out[m] = np.array([float(r["probs"]) for r in rows if r["types"] == m])
    return out


def fits(value, n):
    total = value * n / 10.0
    tol = max(1e-3, abs(total) * 1e-6)
    return abs(total - round(total)) < tol


def solve(values, n_max):
    good = []
    for n in range(1, n_max + 1):
        if all(fits(v, n) for v in values):
            good.append(n)
    return good


def count_near(path, mode):
    atoms = parsePDB(path)
    atoms = atoms.select("occupancy > 0")
    protein = atoms.select("protein")
    other = atoms.select("not protein and not water")
    ca = protein.select("name CA")
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
        for a, h in enumerate(tree.query_ball_point(np.asarray(sel_xyz), r=CUTOFF)):
            if h:
                mask[sel_res[a]] = True
    return int(mask.sum()), len(keys)


def main():
    split = sys.argv[1]
    limit = int(sys.argv[2]) if len(sys.argv) > 2 else 10 ** 9
    vals = load_values(split)
    ids = json.load(open(ROOT + "/repo/training/test_%s.json" % split))
    names = [str(x)[:-4] for x in
             np.load(os.path.join(SD, STEM[split] + "_2.npz"), allow_pickle=True)["names"]]

    if split == "small_molecule":
        cands = [("chain+ligand", lambda nm, pid: ROOT + "/verify/inputs/small_molecule/%s.pdb" % nm)]
    else:
        cands = [("asym", lambda nm, pid: FIXED_5L70["asym"] if pid == "5l70"
                  else ROOT + "/data/structures/asym/%s.pdb" % pid),
                 ("biounit1", lambda nm, pid: FIXED_5L70["biounit1"] if pid == "5l70"
                  else ROOT + "/data/structures/biounit1/%s.pdb" % pid)]

    tally = collections.Counter()
    total = 0
    rows = []
    for i, nm in enumerate(names[:limit]):
        pid = ids[i]
        triple = [vals[m][i] for m in METHODS]
        row = {"name": nm, "values": triple}
        # the authors' own n, from their three published numbers
        sol = solve(triple, 1200)
        row["n_solved"] = sol[:6]
        if not sol:
            rows.append(row)
            continue
        total += 1
        for label, pathf in cands:
            for mode in ("any_atom", "sidechain"):
                try:
                    n, nres = count_near(pathf(nm, pid), mode)
                except Exception as err:
                    row["%s/%s" % (label, mode)] = "ERR %s" % type(err).__name__
                    continue
                row["%s/%s" % (label, mode)] = n
                row["n_residues_%s" % label] = nres
                if n in sol:
                    tally["%s/%s" % (label, mode)] += 1
        rows.append(row)
        if (i + 1) % 25 == 0:
            print("  ...", i + 1, "/", len(names), flush=True)

    print("\n=== %s: candidate n matches the authors' solved n ===" % split)
    print("    (%d of %d proteins had a solvable n)" % (total, len(names[:limit])))
    for k, v in tally.most_common():
        print("    %-24s %3d / %3d  (%.0f%%)" % (k, v, total, 100.0 * v / total))

    print("\n  first 10 proteins:")
    for row in rows[:10]:
        extra = " ".join("%s=%s" % (k.split("/")[0][:4] + "/" + k.split("/")[1][:3], row[k])
                         for k in row if "/" in k)
        print("    %-12s solved_n=%-18s %s" % (row["name"], row["n_solved"], extra))

    with open(ROOT + "/verify/out/solve_n_%s.json" % split, "w") as fh:
        json.dump({"tally": dict(tally), "n_solvable": total, "rows": rows},
                  fh, indent=1, default=float)


if __name__ == "__main__":
    sys.exit(main())
