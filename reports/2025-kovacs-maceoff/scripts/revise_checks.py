"""Checks for the revision after the adversarial review (REVIEW.md, findings 1-4, 10-11).

CPU only, no model. Reads the released xyz once for the per-atom force norm
(the per-config CSVs only hold the largest Cartesian component), then joins on index.
Every count quoted in the revised REPORT.md comes from this log.
"""
import csv
import os
import re

import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
XYZ = os.path.join(ROOT, "data", "test_extract", "test_large_neut_all.xyz")
KEYS = ("small", "medium", "large")
SUBSETS = ("PubChem", "DES370K Monomers", "DES370K Dimers", "Dipeptides",
           "Solvated Amino Acids", "water", "QMugs")
PUB_N = {"PubChem": 33884, "DES370K Dimers": 13896}

claims = __import__("json").load(open(os.path.join(ROOT, "claims.json")))["claims"]
MK = {"MACE-OFF23(S)": "small", "MACE-OFF23(M)": "medium", "MACE-OFF23(L)": "large"}

# Per-atom norm and SMILES straight from the xyz
ctype_re = re.compile(r'config_type=(?:"([^"]*)"|(\S+))')
smiles_re = re.compile(r'smiles="([^"]*)"')
max_norm, smiles, ctype_x = [], [], []
with open(XYZ) as fh:
    while True:
        line = fh.readline()
        if not line:
            break
        nat = int(line)
        com = fh.readline()
        m = ctype_re.search(com)
        ctype_x.append(m.group(1) or m.group(2))
        s = smiles_re.search(com)
        smiles.append(s.group(1) if s else "")
        f = np.array([[float(x) for x in fh.readline().split()[4:7]] for _ in range(nat)])
        max_norm.append(np.linalg.norm(f, axis=1).max())
max_norm = np.array(max_norm)


def load(key):
    rows = list(csv.DictReader(open(os.path.join(ROOT, "runs", "out", f"errors_{key}.csv"))))
    idx = np.array([int(r["index"]) for r in rows])
    assert (idx == np.arange(len(idx))).all(), key
    return {
        "ct": np.array([r["config_type"] for r in rows]),
        "nat": np.array([int(r["n_atoms"]) for r in rows]),
        "e": np.array([float(r["abs_e_err_per_atom_eV"]) for r in rows]),
        "f": np.array([float(r["sum_abs_f_comp_err_eV_A"]) for r in rows]),
        "comp": np.array([float(r["ref_max_abs_f_eV_A"]) for r in rows]),
        "sumf": np.array([float(r["ref_sum_f_norm_eV_A"]) for r in rows]),
    }


D = {k: load(k) for k in KEYS}
assert (D["small"]["ct"] == np.array(ctype_x)).all()
ct = D["small"]["ct"]
comp = D["small"]["comp"]
sumf = D["small"]["sumf"]


def mae(d, sub, keep):
    m = (d["ct"] == sub) & keep
    return d["e"][m].mean() * 1000, d["f"][m].sum() / (3 * d["nat"][m].sum()) * 1000, int(m.sum())


def score(keep, label):
    n_round = 0
    out = []
    for c in claims:
        e, f, n = mae(D[MK[c["model"]]], c["subset"], keep)
        v = e if c["metric"] == "energy_mae" else f
        ok = round(v, 2) == round(c["paper"], 2)
        n_round += ok
        out.append((c["id"], c["paper"], v, ok))
    print(f"[{label}] {n_round}/42 round to the published value")
    for i, p, v, ok in out:
        if not ok:
            print(f"    miss {i:30s} paper {p:6.2f}  ours {v:9.4f}")
    return n_round


allk = np.ones(len(ct), bool)
print("== Summary counts, released file as is")
rel = []
for c in claims:
    e, f, _ = mae(D[MK[c["model"]]], c["subset"], allk)
    v = e if c["metric"] == "energy_mae" else f
    rel.append((c["id"], c["paper"], v, 100 * (v - c["paper"]) / c["paper"]))
print("within 0.5%:", sum(abs(r[3]) <= 0.5 for r in rel))
print("within 5%  :", sum(abs(r[3]) <= 5.0 or abs(r[2] - r[1]) <= (0.02 if r[0][0] == "E" else 0.2) for r in rel))
print("outside 0.5%:")
for r in rel:
    if abs(r[3]) > 0.5:
        print(f"    {r[0]:30s} paper {r[1]:6.2f} ours {r[2]:9.4f}  {r[3]:+6.2f}%")
print("outside 5% (no floor applies):")
for r in rel:
    tol = max(0.05 * r[1], 0.02 if r[0][0] == "E" else 0.2)
    if abs(r[2] - r[1]) > tol:
        print(f"    {r[0]:30s} {r[3]:+6.2f}%")
score(allk, "no cut")
print("values at 4 decimals:")
for r in rel:
    print(f"    {r[0]:30s} {r[2]:.4f}")

print("\n== Cut on the largest Cartesian component vs per-atom norm")
for name, arr, cut in (("component", comp, 10.0), ("per-atom norm", max_norm, 10.0)):
    keep = arr <= cut
    cnt = {s: int(((ct == s) & keep).sum()) for s in SUBSETS}
    print(f"{name} <= {cut}: {cnt}")
    score(keep, f"{name} <= {cut}")

# Window of component cuts that hits both published counts
cand = np.unique(comp[(ct == "PubChem") | (ct == "DES370K Dimers")])
ok = []
for t in cand[(cand > 9.9) & (cand < 10.1)]:
    for x in (t - 1e-9, t):
        k = comp <= x
        if all(int(((ct == s) & k).sum()) == n for s, n in PUB_N.items()):
            ok.append(x)
lo_vals = sorted(v for v in cand if v <= 10.0)
hi_vals = sorted(v for v in cand if v > 10.0)
print(f"component window: largest kept value {lo_vals[-1]:.4f}, smallest dropped {hi_vals[0]:.4f}")
for s in SUBSETS:
    m = ct == s
    print(f"   {s:22s} n={int(m.sum())} dropped at comp<=10: {int((m & (comp > 10)).sum())}")

# Per-atom norm cuts that hit both counts
print("\nper-atom norm cuts that give both published counts:")
nvals = np.unique(max_norm[(ct == "PubChem") | (ct == "DES370K Dimers")])
hits = []
for t in nvals[(nvals > 9) & (nvals < 15)]:
    k = max_norm <= t
    if all(int(((ct == s) & k).sum()) == n for s, n in PUB_N.items()):
        hits.append(t)
if hits:
    print(f"   kept-max range {min(hits):.4f} .. {max(hits):.4f}")
    t = hits[0]
    k = max_norm <= t
    diff = int(((comp <= 10.0) != k).sum())
    print(f"   at {t:.4f}: other subsets {[int(((ct == s) & k).sum()) for s in SUBSETS]}, "
          f"configs differing from the component cut: {diff}")
    score(k, f"per-atom norm <= {t:.4f}")
else:
    print("   none")

print("\nPubChem and Dimers MAE, component cut <= 10:")
kc = comp <= 10.0
for key in KEYS:
    for s in ("PubChem", "DES370K Dimers"):
        e, f, n = mae(D[key], s, kc)
        print(f"   {key:6s} {s:16s} n={n} E={e:.4f} F={f:.4f}")

print("\n== A2: SPICE v2 filters, component vs per-atom norm")
for name, arr in (("component", comp), ("per-atom norm", max_norm)):
    for with_sum in (False, True):
        keep = (arr <= 15.0) & ((sumf <= 0.1) if with_sum else True)
        drop = {s: int(((ct == s) & ~keep).sum()) for s in ("PubChem", "DES370K Dimers")}
        print(f"{name} <=15{' & |sumF|<=0.1' if with_sum else ''}: dropped {drop}")
        if with_sum:
            for key in KEYS:
                e, f, n = mae(D[key], "PubChem", keep)
                print(f"   {key:6s} PubChem n={n} E={e:.4f} F={f:.4f}")
# What issue #7 counted: the extra 209 PubChem points that fail max-norm > 15
print("PubChem configs with per-atom norm > 15:", int(((ct == "PubChem") & (max_norm > 15)).sum()))

print("\n== Per-snapshot split (issue #7, point 3): test side only")
for s in SUBSETS:
    m = ct == s
    sm = [smiles[i] for i in np.where(m)[0] if smiles[i]]
    print(f"   {s:22s} configs={int(m.sum())} with smiles={len(sm)} distinct={len(set(sm))}")
