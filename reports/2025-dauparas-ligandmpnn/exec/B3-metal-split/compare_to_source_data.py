"""Per-protein comparison with the authors' Source Data Fig. 2 (metal panel).

Row i of s2/fig_2_3_1.csv within each method block matches entry i of
training/test_metal.json (definition 'row_order_matches_test_lists'). This is a
check on the metric, not an input to it: the medians are already fixed by score.py.

Usage: compare_to_source_data.py <flavor>
"""

import csv
import json
import sys

import numpy as np

ROOT = "/mnt/e/Ciencia/pipeline/2025-dauparas-ligandmpnn"
EXEC = ROOT + "/exec/B3-metal-split"
SD = ROOT + "/sources/sd/x/s2/fig_2_3_1.csv"

flavor = sys.argv[1] if len(sys.argv) > 1 else "biounit1"
ids = json.load(open(ROOT + "/repo/training/test_metal.json"))

authors = {}
with open(SD) as fh:
    for row in csv.DictReader(fh):
        authors.setdefault(row["types"], []).append(float(row["probs"]))

report = {}
for tag, author_key in (("lmpnn", "LigandMPNN"), ("pmpnn", "ProteinMPNN")):
    ours = json.load(open("%s/recovery_%s_%s.json" % (EXEC, tag, flavor)))
    theirs = authors[author_key]
    assert len(theirs) == len(ids) == len(ours["per_protein"])
    a = np.array([r["recovery"] for r in ours["per_protein"]], dtype=float)
    b = np.array(theirs, dtype=float)
    ok = ~np.isnan(a)
    diff = a[ok] - b[ok]
    report[tag] = {
        "author_median": float(np.median(b)),
        "our_median": float(np.median(a[ok])),
        "pearson_r": float(np.corrcoef(a[ok], b[ok])[0, 1]),
        "mean_abs_diff_pp": float(np.mean(np.abs(diff))),
        "median_abs_diff_pp": float(np.median(np.abs(diff))),
        "worst": sorted(
            ({"id": ids[i], "ours": a[i], "theirs": b[i]}
             for i in np.where(ok)[0]),
            key=lambda d: -abs(d["ours"] - d["theirs"]))[:10],
    }
    print(tag, {k: v for k, v in report[tag].items() if k != "worst"})
    for w in report[tag]["worst"][:5]:
        print("   %s ours=%.2f theirs=%.2f" % (w["id"], w["ours"], w["theirs"]))

json.dump(report, open("%s/compare_source_data_%s.json" % (EXEC, flavor), "w"),
          indent=1, default=float)
