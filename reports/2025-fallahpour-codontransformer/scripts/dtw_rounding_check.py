"""Why our normalized DTW differs from the authors' in the 3rd decimal.

The %MinMax profiles deposited in the workbook carry two decimals, so a per-item exact
match is impossible. This measures the size of that effect: add uniform noise of +/-0.005
(the quantisation half-step) to the published profiles and look at how much the
normalized DTW distance moves.
"""
import csv
import os
import re
import sys

import numpy as np
import openpyxl
from dtw import dtw

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WB = os.path.join(ROOT, "data", "sourcedata", "unzipped", "Source Data",
                  "Fig. 4, Supplementary Fig. 19f-h, 20, 21, 22 and 25.xlsx")
BASE = "Base Codon- Transformer"
FINE = "Fine-tuned Codon- Transformer"


def norm(s):
    return re.sub(r"\s+", " ", str(s).replace("\xa0", " ")).strip()


wb = openpyxl.load_workbook(WB, read_only=True, data_only=True)
ws = wb["%MinMax"]
it = ws.iter_rows(values_only=True)
head = [str(h) for h in next(it)]
prof = {}
decimals = set()
for raw in it:
    if all(c is None for c in raw):
        continue
    r = dict(zip(head, raw))
    txt = str(r["minmax"])
    for tok in txt.split(",")[:200]:
        if "." in tok:
            decimals.add(len(tok.split(".")[1]))
    prof[(r["organism"], r["protein (benchmark)"], norm(r["model"]))] = np.array(
        [float(x) for x in txt.split(",") if x not in ("", "NA")])
wb.close()
print("decimal places found in the deposited %MinMax values:", sorted(decimals))

keys = sorted({(o, p) for (o, p, m) in prof if m == BASE})
rng = np.random.default_rng(123)
shifts = []
for o, p in keys:
    a, b = prof[(o, p, BASE)], prof[(o, p, FINE)]
    d0 = dtw(a, b).normalizedDistance
    for _ in range(3):
        da = dtw(a + rng.uniform(-0.005, 0.005, a.size),
                 b + rng.uniform(-0.005, 0.005, b.size)).normalizedDistance
        shifts.append(abs(da - d0))
s = np.array(shifts)
print(f"effect of +/-0.005 quantisation noise on the normalized DTW distance: "
      f"n={s.size} mean={s.mean():.2e} p95={np.percentile(s, 95):.2e} max={s.max():.2e}")
# Observed differences, read from the L2 output instead of typed in
# (the first version of this line carried a hand-written "mean ~5e-4", which was wrong)
csv_path = os.path.join(ROOT, "runs", "out", "l1_l2_per_protein.csv")
with open(csv_path, newline="") as fh:
    diffs = np.array([float(row["dtw_ours"]) - float(row["dtw_authors"])
                      for row in csv.DictReader(fh)])
print(f"observed ours - authors per protein (from the L2 run): n={diffs.size} "
      f"mean |diff|={np.abs(diffs).mean():.3e} max |diff|={np.abs(diffs).max():.3e} "
      f"mean signed={diffs.mean():+.3e} below zero={(diffs < 0).sum()}/{diffs.size}")
sys.exit(0)
