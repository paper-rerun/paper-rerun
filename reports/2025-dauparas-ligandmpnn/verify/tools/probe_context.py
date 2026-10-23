"""What did the authors count as "the context" on the nucleotide and metal splits?

The solved denominators are far too small for "any non-protein atom": 1dwh comes
out at 3 where every hetero atom in the file gives 122, and that file is full of
sugars, sulfates and glycerol. Three residues is what you get around a single
calcium. So the context was probably the metal alone on the metal split, and the
nucleic acid alone on the nucleotide split, not every hetero atom as the Results
sentence says.

Each variant below is scored the same way: residues (any atom, the reading the
small-molecule split already confirmed) within 5.0 A of the chosen context.
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
METHODS = ["Rosetta", "ProteinMPNN", "LigandMPNN"]
STEM = {"nucleotide": "fig_2_2", "metal": "fig_2_3"}

TRANSITION = set("SC TI V CR MN FE CO NI CU ZN Y ZR NB MO TC RU RH PD AG CD "
                 "HF TA W RE OS IR PT AU HG".split())
OTHER_METAL = set("LI NA K RB CS BE MG CA SR BA AL GA IN TL SN PB BI LA CE SM EU GD TB YB LU U".split())
ALL_METAL = TRANSITION | OTHER_METAL


def fits(value, n):
    t = value * n / 10.0
    return abs(t - round(t)) < max(1e-3, abs(t) * 1e-6)


def smallest_n(values, n_max=1500):
    for n in range(1, n_max + 1):
        if all(fits(v, n) for v in values):
            return n
    return None


def counts_for(path, variants):
    atoms = parsePDB(path).select("occupancy > 0")
    protein = atoms.select("protein")
    nonprot = atoms.select("not protein and not water")
    ca = protein.select("name CA")
    keys = list(zip(ca.getChids(), ca.getResnums(), [str(i) for i in ca.getIcodes()]))
    index = {}
    for i, k in enumerate(keys):
        index.setdefault(k, i)

    p_el = np.array([str(e).strip().upper() for e in protein.getElements()])
    p_keys = list(zip(protein.getChids(), protein.getResnums(),
                      [str(i) for i in protein.getIcodes()]))
    p_xyz = np.asarray(protein.getCoords(), float)
    p_ok = ~np.isin(p_el, ["H", "D"])

    nucleic = atoms.select("nucleic")
    out = {}
    for name in variants:
        if name == "all_nonprotein":
            sel = nonprot
            xyz = None if sel is None else np.asarray(sel.getCoords(), float)
            el = None if sel is None else np.array([str(e).strip().upper() for e in sel.getElements()])
        elif name == "nucleic_only":
            sel = nucleic
            xyz = None if sel is None else np.asarray(sel.getCoords(), float)
            el = None if sel is None else np.array([str(e).strip().upper() for e in sel.getElements()])
        elif name in ("metal_all", "metal_transition"):
            if nonprot is None:
                out[name] = 0
                continue
            el_all = np.array([str(e).strip().upper() for e in nonprot.getElements()])
            want = ALL_METAL if name == "metal_all" else TRANSITION
            keep = np.isin(el_all, list(want))
            xyz = np.asarray(nonprot.getCoords(), float)[keep]
            el = el_all[keep]
        else:
            raise ValueError(name)

        if xyz is None or len(xyz) == 0:
            out[name] = 0
            continue
        xyz = xyz[~np.isin(el, ["H", "D"])] if el is not None else xyz
        if len(xyz) == 0:
            out[name] = 0
            continue
        tree = cKDTree(xyz)
        res = set()
        sub = p_xyz[p_ok]
        subk = [k for k, ok in zip(p_keys, p_ok) if ok]
        for a, h in enumerate(tree.query_ball_point(sub, r=CUTOFF)):
            if h and subk[a] in index:
                res.add(subk[a])
        out[name] = len(res)
    return out


def main():
    split = sys.argv[1]
    variants = (["all_nonprotein", "nucleic_only"] if split == "nucleotide"
                else ["all_nonprotein", "metal_all", "metal_transition"])
    rows = list(csv.DictReader(open(os.path.join(SD, STEM[split] + "_1.csv"))))
    vals = {m: np.array([float(r["probs"]) for r in rows if r["types"] == m]) for m in METHODS}
    ids = json.load(open(ROOT + "/repo/training/test_%s.json" % split))
    fixed = {"asym": ROOT + "/verify/inputs/fixed/5l70_asym.pdb",
             "biounit1": ROOT + "/verify/inputs/fixed/5l70_biounit1.pdb"}

    tally = collections.Counter()
    detail = []
    for i, pid in enumerate(ids):
        n_true = smallest_n([vals[m][i] for m in METHODS])
        row = {"id": pid, "n_true": n_true}
        for flav in ("asym", "biounit1"):
            path = fixed[flav] if pid == "5l70" else \
                "%s/data/structures/%s/%s.pdb" % (ROOT, flav, pid)
            try:
                c = counts_for(path, variants)
            except Exception as err:
                row[flav] = "ERR %s" % type(err).__name__
                continue
            row[flav] = c
            for k, v in c.items():
                if n_true is not None and v == n_true:
                    tally["%s/%s" % (flav, k)] += 1
        detail.append(row)
        if (i + 1) % 25 == 0:
            print("  ...", i + 1, "/", len(ids), flush=True)

    n = sum(1 for r in detail if r["n_true"] is not None)
    print("\n=== %s: context variant reproduces the authors' n ===" % split)
    for k, v in tally.most_common():
        print("    %-28s %3d / %3d  (%.0f%%)" % (k, v, n, 100.0 * v / n))
    print("\n  first 10:")
    for r in detail[:10]:
        print("    %-6s n_true=%-5s asym=%s" % (r["id"], r["n_true"], r.get("asym")))

    with open(ROOT + "/verify/out/probe_context_%s.json" % split, "w") as fh:
        json.dump({"tally": dict(tally), "detail": detail}, fh, indent=1, default=str)


if __name__ == "__main__":
    sys.exit(main())
