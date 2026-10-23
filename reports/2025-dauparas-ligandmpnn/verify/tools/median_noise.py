"""How precise is the published median, given the split sizes?

The claim sheet derives its tolerance from the paper's rounding plus sampling.
It never asks how much the median itself moves. On the metal split the scored
sets are tiny - the authors' own counts solve to 1, 3, 4, 12 residues - so a
per-protein value can only land on a few discrete points, and a median over 83
of them is coarse. This bootstraps the median of the authors' OWN published
per-protein values, which gives the precision of their published number without
using anything of ours.
"""

import csv
import json
import os

import numpy as np

ROOT = "/mnt/e/Ciencia/pipeline/2025-dauparas-ligandmpnn"
SD = ROOT + "/sources/sd/x/s2"
STEM = {"small_molecule": "fig_2_1", "nucleotide": "fig_2_2", "metal": "fig_2_3"}

rng = np.random.default_rng(20261022)
out = {}

print("%-16s %-12s %-6s %-9s %-22s %s" %
      ("split", "method", "n", "median", "bootstrap 95% CI", "CI half-width"))
print("-" * 86)
for split in ("small_molecule", "nucleotide", "metal"):
    path = os.path.join(SD, STEM[split] + "_1.csv")
    rows = list(csv.DictReader(open(path)))
    for method in ("Rosetta", "ProteinMPNN", "LigandMPNN"):
        v = np.array([float(r["probs"]) for r in rows if r["types"] == method])
        boot = np.median(rng.choice(v, size=(20000, len(v)), replace=True), axis=1)
        lo, hi = np.percentile(boot, [2.5, 97.5])
        half = (hi - lo) / 2
        print("%-16s %-12s %-6d %-9.3f [%7.3f, %7.3f]   +-%.2f pp"
              % (split, method, len(v), np.median(v), lo, hi, half))
        out["%s/%s" % (split, method)] = {
            "n": int(len(v)), "median": float(np.median(v)),
            "ci95_low": float(lo), "ci95_high": float(hi),
            "ci95_half_width": float(half),
            "n_distinct_values": int(len(set(v.round(4)))),
        }

with open(ROOT + "/verify/out/median_noise.json", "w") as fh:
    json.dump(out, fh, indent=1)
print("\nwrote verify/out/median_noise.json")
