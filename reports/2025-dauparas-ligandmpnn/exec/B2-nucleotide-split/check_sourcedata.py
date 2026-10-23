"""Re-reads the authors' Source Data for Fig. 2 nucleotide panel, so our 74 per-protein
values can be put next to theirs one by one, not only median against median."""
import json
import os

import numpy as np
import csv

ROOT = "/mnt/e/Ciencia/pipeline/2025-dauparas-ligandmpnn"
sd = os.path.join(ROOT, "sources/sd/x/s2")
rows = list(csv.DictReader(open(os.path.join(sd, "fig_2_2_1.csv"))))
print(list(rows[0].keys()), len(rows))
groups = {}
for r in rows:
    groups.setdefault(r["types"], []).append(float(r["probs"]))
for t, v in groups.items():
    print(f"{t}: n={len(v)} median={np.median(v):.3f} mean={np.mean(v):.3f}")

z = np.load(os.path.join(sd, "fig_2_2_2.npz"), allow_pickle=True)
print("npz keys:", list(z.keys()))
names = [str(x) for x in z["names"]]
ids = json.load(open(os.path.join(ROOT, "repo/training/test_nucleotide.json")))
print("names == test list order:", names == ids, len(names))
for k in z.keys():
    if k != "names":
        v = z[k]
        print(k, np.shape(v), v if np.size(v) < 4 else "")

order = {"ids": ids}
for t, v in groups.items():
    order[t] = v
json.dump(order, open(os.path.join(ROOT, "exec/B2-nucleotide-split", "authors_fig2a_nucleotide.json"), "w"), indent=1)
print("saved authors per-protein values")
