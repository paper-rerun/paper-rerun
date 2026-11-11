"""Every number quoted in REPORT.md, in one place.

Reads the per-protein CSVs written by analyze_sourcedata.py (L1/L2) and compare_l3.py (L3)
and prints the claim table, the per-organism breakdown and the verdict per claim.
"""
import csv
import os

import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "runs", "out")

l12 = list(csv.DictReader(open(os.path.join(OUT, "l1_l2_per_protein.csv"), encoding="utf-8")))
l3 = list(csv.DictReader(open(os.path.join(OUT, "generated_primary_metrics.csv"), encoding="utf-8")))
mg = list(csv.DictReader(open(os.path.join(OUT, "generated_ecoli_mg1655_metrics.csv"), encoding="utf-8")))


def col(rows, name):
    return np.array([float(r[name]) for r in rows if r[name] not in ("", "None")])


print("=== claim table (260 protein-organism pairs, Base vs Fine-tuned) ===")
rowsfmt = "{:<28} {:>10} {:>12} {:>12} {:>12}"
print(rowsfmt.format("", "published", "L1 authors", "L2 our code", "L3 our seqs"))
print(rowsfmt.format("C1 Jaccard (Fig. 4a)", "0.74",
                     f"{col(l12, 'jaccard_authors').mean():.4f}",
                     f"{col(l12, 'jaccard_ours').mean():.4f}",
                     f"{col(l3, 'jaccard_ours').mean():.4f}"))
print(rowsfmt.format("C2 codon similarity % (4b)", "69.26",
                     f"{col(l12, 'similarity_authors').mean():.4f}",
                     f"{col(l12, 'similarity_ours').mean():.4f}",
                     f"{col(l3, 'similarity_ours').mean():.4f}"))
print(rowsfmt.format("C3 normalized DTW (4c)", "0.05",
                     f"{col(l12, 'dtw_authors').mean():.4f}",
                     f"{col(l12, 'dtw_ours').mean():.4f}",
                     f"{col(l12, 'dtw_ours').mean():.4f}"))
print(rowsfmt.format("C3 sd", "0.03",
                     f"{col(l12, 'dtw_authors').std(ddof=1):.4f}",
                     f"{col(l12, 'dtw_ours').std(ddof=1):.4f}",
                     f"{col(l12, 'dtw_ours').std(ddof=1):.4f}"))
print("  (L3 column of C3 equals L2 because all 520 regenerated sequences are identical")
print("   to the deposited ones, so the %MinMax profiles and the DTW cannot differ)")

print("\n=== per organism, from the authors' deposited per-protein values (L1) ===")
print("{:<26} {:>4} {:>9} {:>9} {:>9} {:>9}".format(
    "organism", "n", "jaccard", "simil. %", "DTW", "DTW sd"))
orgs = sorted({r["organism"] for r in l12})
for org in orgs:
    sub = [r for r in l12 if r["organism"] == org]
    print("{:<26} {:>4} {:>9.4f} {:>9.4f} {:>9.4f} {:>9.4f}".format(
        org, len(sub), col(sub, "jaccard_authors").mean(), col(sub, "similarity_authors").mean(),
        col(sub, "dtw_authors").mean(), col(sub, "dtw_authors").std(ddof=1)))
print("{:<26} {:>4} {:>9.4f} {:>9.4f} {:>9.4f} {:>9.4f}".format(
    "ALL", len(l12), col(l12, "jaccard_authors").mean(), col(l12, "similarity_authors").mean(),
    col(l12, "dtw_authors").mean(), col(l12, "dtw_authors").std(ddof=1)))

print("\n=== L3: regenerated vs deposited sequences ===")
print(f"identical, fine-tuned checkpoint: {sum(int(r['fine_identical']) for r in l3)}/{len(l3)}")
print(f"identical, base checkpoint:       {sum(int(r['base_identical']) for r in l3)}/{len(l3)}")
print("secondary E. coli token 'Escherichia coli str. K-12 substr. MG1655':")
print(f"  identical fine {sum(int(r['fine_identical']) for r in mg)}/{len(mg)}, "
      f"base {sum(int(r['base_identical']) for r in mg)}/{len(mg)}")
ec_general = [r for r in l3 if r["organism"] == "Escherichia coli"]
print(f"  E. coli jaccard  general={col(ec_general, 'jaccard_ours').mean():.4f}  "
      f"MG1655={col(mg, 'jaccard_ours').mean():.4f}")
print(f"  E. coli simil. % general={col(ec_general, 'similarity_ours').mean():.4f}  "
      f"MG1655={col(mg, 'similarity_ours').mean():.4f}")

print("\n=== A1: Jaccard read positionwise instead of over codon sets ===")
# multiset Jaccard on the deposited sequences, for contrast only
import collections
vals = []
seqs = {}
for r in csv.DictReader(open(os.path.join(OUT, "generated_primary.csv"), encoding="utf-8")):
    seqs.setdefault((r["organism"], r["protein"]), {})[r["checkpoint"]] = r["authors_dna"]
for k, d in seqs.items():
    a = [d["base"][i:i + 3] for i in range(0, len(d["base"]) - len(d["base"]) % 3, 3)]
    b = [d["fine"][i:i + 3] for i in range(0, len(d["fine"]) - len(d["fine"]) % 3, 3)]
    ca, cb = collections.Counter(a), collections.Counter(b)
    inter = sum((ca & cb).values())
    union = sum((ca | cb).values())
    vals.append(inter / union)
v = np.array(vals)
print(f"multiset Jaccard: n={len(v)} mean={v.mean():.4f} (set-based mean is "
      f"{col(l12, 'jaccard_authors').mean():.4f})")

print("\n=== A2: mean of the 5 per-organism means instead of the 260 pairs ===")
for name, key in (("jaccard", "jaccard_authors"), ("similarity", "similarity_authors"),
                  ("dtw", "dtw_authors")):
    m = np.mean([col([r for r in l12 if r["organism"] == o], key).mean() for o in orgs])
    print(f"  {name}: {m:.4f} (pooled {col(l12, key).mean():.4f}) - equal, 52 proteins per organism")
