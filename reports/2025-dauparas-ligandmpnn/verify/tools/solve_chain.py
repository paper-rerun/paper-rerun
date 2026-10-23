"""For the nucleotide and metal splits: was the input one protein chain?

The asymmetric unit matches the authors' solved n on about half the proteins and
biological assembly 1 on the other half, which is what you would see if neither
was the input. The small-molecule split is one chain plus one ligand, so the
obvious thing to test is one chain here too.

For every protein chain of the file, count the near-ligand residues of that chain
alone (context = every non-protein, non-water heavy atom in the file) and ask
whether any chain reproduces the authors' n, and if so which.
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
CUTOFF = 5.0
BACKBONE = {"N", "CA", "C", "O", "OXT"}
METHODS = ["Rosetta", "ProteinMPNN", "LigandMPNN"]
STEM = {"small_molecule": "fig_2_1", "nucleotide": "fig_2_2", "metal": "fig_2_3"}


def fits(value, n):
    total = value * n / 10.0
    return abs(total - round(total)) < max(1e-3, abs(total) * 1e-6)


def smallest_n(values, n_max=1200):
    for n in range(1, n_max + 1):
        if all(fits(v, n) for v in values):
            return n
    return None


def per_chain_counts(path, mode="any_atom", ctx_same_chain=False):
    atoms = parsePDB(path).select("occupancy > 0")
    protein = atoms.select("protein")
    other = atoms.select("not protein and not water")
    if protein is None:
        return {}, 0
    if other is None:
        return {}, 0
    o_el = np.array([str(e).strip().upper() for e in other.getElements()])
    o_keep = ~np.isin(o_el, ["H", "D"])
    o_xyz_all = np.asarray(other.getCoords(), float)[o_keep]
    o_ch_all = np.array(other.getChids())[o_keep]

    names = np.array([str(n).strip() for n in protein.getNames()])
    els = np.array([str(e).strip().upper() for e in protein.getElements()])
    chids = np.array(protein.getChids())
    resnums = np.array(protein.getResnums())
    icodes = np.array([str(i) for i in protein.getIcodes()])
    coords = np.asarray(protein.getCoords(), float)

    keep = ~np.isin(els, ["H", "D"])
    if mode == "sidechain":
        keep &= ~np.isin(names, list(BACKBONE))

    out = {}
    for ch in sorted(set(chids)):
        sel = keep & (chids == ch)
        if not sel.any():
            continue
        o_xyz = o_xyz_all[o_ch_all == ch] if ctx_same_chain else o_xyz_all
        if len(o_xyz) == 0:
            out[ch] = 0
            continue
        tree = cKDTree(o_xyz)
        hit = tree.query_ball_point(coords[sel], r=CUTOFF)
        res = set()
        rk = list(zip(chids[sel], resnums[sel], icodes[sel]))
        for a, h in enumerate(hit):
            if h:
                res.add(rk[a])
        out[ch] = len(res)
    n_ca = len(protein.select("name CA"))
    return out, n_ca


def main():
    split = sys.argv[1]
    rows = list(csv.DictReader(open(os.path.join(SD, STEM[split] + "_1.csv"))))
    vals = {m: np.array([float(r["probs"]) for r in rows if r["types"] == m]) for m in METHODS}
    ids = json.load(open(ROOT + "/repo/training/test_%s.json" % split))
    fixed = {"asym": ROOT + "/verify/inputs/fixed/5l70_asym.pdb",
             "biounit1": ROOT + "/verify/inputs/fixed/5l70_biounit1.pdb"}

    tally = collections.Counter()
    which_chain = collections.Counter()
    detail = []
    solvable = 0

    for i, pid in enumerate(ids):
        triple = [vals[m][i] for m in METHODS]
        n_true = smallest_n(triple)
        row = {"id": pid, "n_true": n_true}
        if n_true is None:
            detail.append(row)
            continue
        solvable += 1
        for flav in ("asym", "biounit1"):
            path = fixed[flav] if pid == "5l70" else \
                "%s/data/structures/%s/%s.pdb" % (ROOT, flav, pid)
            for ctx_same in (False, True):
                key = "%s/chain%s" % (flav, "_ownctx" if ctx_same else "")
                try:
                    counts, n_ca = per_chain_counts(path, "any_atom", ctx_same)
                except Exception as err:
                    row[key] = "ERR"
                    continue
                row[key] = counts
                hits = [c for c, n in counts.items() if n == n_true]
                if hits:
                    tally[key] += 1
                    if not ctx_same:
                        which_chain[(flav, hits[0])] += 1
                # whole-file total, for reference
                if ctx_same is False:
                    row["%s/whole" % flav] = sum(counts.values())
        detail.append(row)
        if (i + 1) % 25 == 0:
            print("  ...", i + 1, "/", len(ids), flush=True)

    print("\n=== %s: does SOME single chain reproduce the authors' n? ===" % split)
    print("    %d of %d proteins have a solvable n" % (solvable, len(ids)))
    for k, v in tally.most_common():
        print("    %-24s %3d / %3d  (%.0f%%)" % (k, v, solvable, 100.0 * v / solvable))
    print("    chain letter that matched (asym, context = whole file):")
    for (flav, ch), v in which_chain.most_common(8):
        if flav == "asym":
            print("        chain %-3s %3d" % (ch, v))

    print("\n  first 8:")
    for row in detail[:8]:
        print("    %-6s n_true=%-5s asym_chains=%-28s biou_chains=%s"
              % (row["id"], row["n_true"],
                 str(row.get("asym/chain"))[:28], str(row.get("biounit1/chain"))[:28]))

    with open(ROOT + "/verify/out/solve_chain_%s.json" % split, "w") as fh:
        json.dump({"tally": {k: v for k, v in tally.items()},
                   "which_chain": {"%s|%s" % k: v for k, v in which_chain.items()},
                   "n_solvable": solvable, "detail": detail}, fh, indent=1, default=str)


if __name__ == "__main__":
    sys.exit(main())
