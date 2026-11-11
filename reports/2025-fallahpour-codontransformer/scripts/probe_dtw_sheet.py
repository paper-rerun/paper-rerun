"""A3: the DTW sheet of the Fig. 4 workbook has a non-zero diagonal. Find out what it holds.

Prints the 6x6 matrix of normalized_distance for a few proteins, checks whether the
value depends only on model1 or only on model2, and checks symmetry. Then recomputes
the whole matrix from the published %MinMax profiles and compares.
"""
import os
import re

import numpy as np
import openpyxl
from dtw import dtw

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WB = os.path.join(ROOT, "data", "sourcedata", "unzipped", "Source Data",
                  "Fig. 4, Supplementary Fig. 19f-h, 20, 21, 22 and 25.xlsx")


def norm_model(s):
    return re.sub(r"\s+", " ", str(s).replace("\xa0", " ")).strip()


def rows(wb, name):
    ws = wb[name]
    it = ws.iter_rows(values_only=True)
    head = [str(h) for h in next(it)]
    for r in it:
        if not all(c is None for c in r):
            yield dict(zip(head, r))


wb = openpyxl.load_workbook(WB, read_only=True, data_only=True)

prof = {}
for r in rows(wb, "%MinMax"):
    prof[(r["organism"], r["protein (benchmark)"], norm_model(r["model"]))] = [
        float(x) for x in str(r["minmax"]).split(",") if x not in ("", "NA")
    ]

mat = {}
for r in rows(wb, "DTW"):
    mat.setdefault((r["organism"], r["protein"]), {})[
        (norm_model(r["model1"]), norm_model(r["model2"]))
    ] = (float(r["distance"]), float(r["normalized_distance"]))

keys = sorted(mat)
print(f"proteins in DTW sheet: {len(keys)}")

row_const = col_const = sym = 0
for k in keys:
    cells = mat[k]
    models = sorted({m for pair in cells for m in pair})
    byrow = {m: {v[1] for (a, b), v in cells.items() if a == m} for m in models}
    bycol = {m: {v[1] for (a, b), v in cells.items() if b == m} for m in models}
    row_const += all(len(s) == 1 for s in byrow.values())
    col_const += all(len(s) == 1 for s in bycol.values())
    sym += all(
        abs(cells[(a, b)][1] - cells[(b, a)][1]) < 1e-12
        for (a, b) in cells if (b, a) in cells
    )
print(f"proteins where the value depends only on model1: {row_const}/{len(keys)}")
print(f"proteins where the value depends only on model2: {col_const}/{len(keys)}")
print(f"proteins whose matrix is symmetric: {sym}/{len(keys)}")

for k in keys[:2]:
    print(f"\n=== {k} ===")
    cells = mat[k]
    models = sorted({m for pair in cells for m in pair})
    print("            " + "".join(f"{m[:11]:>13}" for m in models))
    for a in models:
        line = f"{a[:11]:>11} "
        for b in models:
            v = cells.get((a, b))
            line += f"{v[1]:13.6f}" if v else f"{'-':>13}"
        print(line)
    print("recomputed from the published profiles (upper half):")
    for i, a in enumerate(models):
        line = f"{a[:11]:>11} "
        for j, b in enumerate(models):
            pa, pb = prof.get((k[0], k[1], a)), prof.get((k[0], k[1], b))
            if pa and pb:
                line += f"{dtw(np.array(pa), np.array(pb)).normalizedDistance:13.6f}"
            else:
                line += f"{'-':>13}"
        print(line)

# Does the deposited value for a row equal our DTW of that model against some other model?
print("\nmatching each deposited row value to our recomputed matrix:")
hits = {}
for k in keys:
    cells = mat[k]
    models = sorted({m for pair in cells for m in pair})
    for a in models:
        vals = {v[1] for (x, y), v in cells.items() if x == a}
        if len(vals) != 1:
            continue
        v = vals.pop()
        best, bestd = None, 1e9
        for b in models:
            pa, pb = prof.get((k[0], k[1], a)), prof.get((k[0], k[1], b))
            if not pa or not pb:
                continue
            d = abs(dtw(np.array(pa), np.array(pb)).normalizedDistance - v)
            if d < bestd:
                best, bestd = b, d
        hits[best] = hits.get(best, 0) + 1
print("  closest partner of the single per-row value, counted over all rows:", hits)
wb.close()
