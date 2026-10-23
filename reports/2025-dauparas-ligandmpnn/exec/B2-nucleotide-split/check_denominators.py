"""Identifies the authors' scored-position count for all 74 proteins from their own
Source Data decimals, with no reference to our recovery values.

A per-protein value is a mean of 10 per-sequence recoveries, each k/n * 100, so
value * n * 10 / 100 must be a whole number. The CSV carries 4 decimals, so a tolerance
of 1e-3 * n * 10 / 100 is allowed. For each protein the script lists which candidate n
survives for BOTH LigandMPNN and ProteinMPNN (same positions, same denominator), and
compares that with our two readings of 'near'.
"""
import json
import os
import sys

import numpy as np

ROOT = "/mnt/e/Ciencia/pipeline/2025-dauparas-ligandmpnn"
BLOCK = os.path.join(ROOT, "exec/B2-nucleotide-split")
sys.path.insert(0, os.path.join(ROOT, "repo"))
from data_utils import parse_PDB  # noqa: E402

BACKBONE_IDX = [0, 1, 2, 4]
SC_IDX = [i for i in range(37) if i not in BACKBONE_IDX and i != 36]
ALL_IDX = [i for i in range(37) if i != 36]
CUTOFF = 5.0
FLAVOR = sys.argv[1] if len(sys.argv) > 1 else "biounit1"

theirs = json.load(open(os.path.join(BLOCK, "authors_fig2a_nucleotide.json")))
ids = theirs["ids"]


def counts(pid):
    out, _b, _o, _i, _w = parse_PDB(
        os.path.join(ROOT, "data/structures/" + FLAVOR, pid + ".pdb"), parse_all_atoms=True
    )
    xyz = out["xyz_37"].numpy()
    m = out["xyz_37_m"].numpy().astype(bool)
    Y = out["Y"].numpy()[out["Y_m"].numpy().astype(bool)]
    L = xyz.shape[0]
    res = {}
    for name, idx in (("sc", SC_IDX), ("all", ALL_IDX)):
        pts = xyz[:, idx, :].reshape(-1, 3)
        keep = m[:, idx].reshape(-1)
        owner = np.repeat(np.arange(L), len(idx))[keep]
        pts = pts[keep]
        near = np.zeros(L, dtype=bool)
        for a in range(0, pts.shape[0], 20000):
            blk = pts[a:a + 20000]
            d2 = ((blk[:, None, :] - Y[None, :, :]) ** 2).sum(-1)
            near[owner[a:a + 20000][(d2 <= CUTOFF * CUTOFF).any(1)]] = True
        res[name] = int(near.sum())
    return res


def candidates(values, nmax=600):
    """n values consistent with every one of the three methods' per-protein numbers"""
    ok = []
    for n in range(1, nmax + 1):
        good = True
        for v in values:
            x = v * n / 10.0
            if abs(x - round(x)) > 3e-5 * abs(x) + 1e-6:
                good = False
                break
        if good:
            ok.append(n)
    return ok


hit_all = hit_sc = 0
rows = []
for k, pid in enumerate(ids):
    vals = [theirs[t][k] for t in ("Rosetta", "ProteinMPNN", "LigandMPNN")]
    cand = candidates(vals)
    c = counts(pid)
    # the smallest surviving candidate is the denominator; multiples of it also survive
    smallest = cand[0] if cand else None
    ok_all = c["all"] in cand
    ok_sc = c["sc"] in cand
    hit_all += ok_all
    hit_sc += ok_sc
    rows.append(dict(id=pid, n_sc=c["sc"], n_all=c["all"], implied=smallest,
                     all_matches=bool(ok_all), sc_matches=bool(ok_sc)))
    print(f"{pid}: sc={c['sc']:4d} all={c['all']:4d} implied={smallest} "
          f"{'ALL' if ok_all else ''}{'SC' if ok_sc else ''}")

print(f"\nimplied denominator == our all-atom count: {hit_all}/74")
print(f"implied denominator == our side-chain count: {hit_sc}/74")
print("proteins where the all-atom count is NOT consistent:",
      [r["id"] for r in rows if not r["all_matches"]])
json.dump(rows, open(os.path.join(BLOCK, "denominator_check_" + FLAVOR + ".json"), "w"), indent=1)
