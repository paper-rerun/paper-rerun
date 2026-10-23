"""Recover the authors' number of scored positions per protein from Source Data.

Each per-protein value is (matches)/(10 * n_near) * 100, so the three methods'
values for one protein share the denominator 10 * n_near. Search n_near.
"""
import csv
import json
import os

import numpy as np

SD = "/mnt/e/Ciencia/pipeline/2025-dauparas-ligandmpnn/sources/sd/x/s2"
BASE = "/mnt/e/Ciencia/pipeline/2025-dauparas-ligandmpnn/exec/B1-small-molecule-split"

z = np.load(os.path.join(SD, "fig_2_1_2.npz"), allow_pickle=True)
names = [str(n)[:-4] for n in z["names"]]
ros = np.array(z["p1x"], dtype=float)
lig = np.array(z["p1y"], dtype=float)
rows = list(csv.DictReader(open(os.path.join(SD, "fig_2_1_1.csv"))))
pmp = np.array([float(r["probs"]) for r in rows if r["types"] == "ProteinMPNN"])

mine = json.load(open(os.path.join(BASE, "near_mask.json")))

out = {}
for i, n in enumerate(names):
    vals = np.array([ros[i], lig[i], pmp[i]]) / 100.0
    best, best_err = None, 1e9
    for d in range(1, 301):
        k = vals * 10 * d
        err = np.abs(k - np.round(k)).max()
        if err < best_err - 1e-9:
            best, best_err = d, err
    out[n] = {"inferred": best, "err": float(best_err), "ours": mine[n]["n_near"]}

good = [v for v in out.values() if v["err"] < 2e-3]
print("proteins with a clean denominator:", len(good), "/", len(out))
inf = np.array([v["inferred"] for v in out.values()])
our = np.array([v["ours"] for v in out.values()])
print("inferred n_near : min %d median %d max %d" % (inf.min(), np.median(inf), inf.max()))
print("ours            : min %d median %d max %d" % (our.min(), np.median(our), our.max()))
print("exact match:", int((inf == our).sum()), " ours smaller:", int((our < inf).sum()),
      " ours larger:", int((our > inf).sum()))
json.dump(out, open(os.path.join(BASE, "inferred_n_near.json"), "w"), indent=1)
for n in names[:10]:
    print(n, out[n])
