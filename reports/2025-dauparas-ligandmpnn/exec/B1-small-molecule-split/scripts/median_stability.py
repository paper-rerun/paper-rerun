"""How much the headline median moves with the sampling, at no extra GPU cost.

Two checks on the designs already made:
  - split the 10 sequences per protein into the two disjoint halves of 5 and take
    the median of each (the per-protein value is a mean over sequences, so this
    is a real resample of the sampling noise, not of the protein set);
  - bootstrap the 317 proteins, 2000 draws, to get the spread the protein set
    itself contributes.
"""
import json
import os

import numpy as np

BASE = "/mnt/e/Ciencia/pipeline/2025-dauparas-ligandmpnn/exec/B1-small-molecule-split"
res = json.load(open(os.path.join(BASE, "results.json")))
rng = np.random.default_rng(7)

out = {}
for claim in res:
    out[claim] = {}
    for label in ["sidechain_within_5A", "any_heavy_atom_within_5A"]:
        per = res[claim][label]["per_protein"]
        stems = list(per)
        seqs = np.array([per[s]["per_sequence"] for s in stems])   # [317, 10]
        full = np.median(seqs.mean(1))
        h1 = np.median(seqs[:, :5].mean(1))
        h2 = np.median(seqs[:, 5:].mean(1))
        boot = np.array([np.median(seqs.mean(1)[rng.integers(0, len(stems), len(stems))])
                         for _ in range(2000)])
        out[claim][label] = {
            "median_all_10": float(full),
            "median_first_5": float(h1),
            "median_last_5": float(h2),
            "half_split_spread_pp": float(abs(h1 - h2)),
            "bootstrap_sd_pp": float(boot.std()),
            "bootstrap_ci95": [float(np.percentile(boot, 2.5)), float(np.percentile(boot, 97.5))],
        }
        print("%s %-26s median %.3f | halves %.3f / %.3f | bootstrap sd %.2f pp"
              % (claim, label, full, h1, h2, boot.std()))
json.dump(out, open(os.path.join(BASE, "median_stability.json"), "w"), indent=1)
