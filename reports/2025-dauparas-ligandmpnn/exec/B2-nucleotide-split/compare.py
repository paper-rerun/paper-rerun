"""Puts our 74 per-protein values next to the authors' Source Data values, one by one.
Row i of the Source Data is entry i of training/test_nucleotide.json (checked, the npz
'names' array is the same ids in the same order with a '.pdb' suffix)."""
import json
import os
import sys

import numpy as np

ROOT = "/mnt/e/Ciencia/pipeline/2025-dauparas-ligandmpnn"
BLOCK = os.path.join(ROOT, "exec/B2-nucleotide-split")
flavor = sys.argv[1]

ours = json.load(open(os.path.join(BLOCK, f"results_{flavor}.json")))
theirs = json.load(open(os.path.join(BLOCK, "authors_fig2a_nucleotide.json")))
ids = theirs["ids"]

for tag, paper in (("LigandMPNN", 50.5), ("ProteinMPNN", 34.0)):
    if tag not in ours:
        continue
    d = {r["id"]: r for r in ours[tag]["detail"]}
    mine = np.array([d[i]["recovery"] for i in ids])
    auth = np.array([theirs[tag][k] for k in range(len(ids))])
    diff = mine - auth
    print(f"--- {tag} ({flavor}) ---")
    print(f"paper median {paper}  authors' source data median {np.median(auth):.3f}  ours {np.median(mine):.3f}")
    print(f"mean ours {mine.mean():.3f}  mean theirs {auth.mean():.3f}")
    print(f"per-protein: pearson r={np.corrcoef(mine, auth)[0,1]:.3f}  "
          f"median |diff|={np.median(np.abs(diff)):.2f}  within 5pp: {(np.abs(diff)<=5).sum()}/74  "
          f"within 10pp: {(np.abs(diff)<=10).sum()}/74")
    worst = np.argsort(-np.abs(diff))[:8]
    for k in worst:
        print(f"   {ids[k]}: ours {mine[k]:.2f} theirs {auth[k]:.2f} diff {diff[k]:+.2f} "
              f"near={d[ids[k]]['n_near_bb_ok']} res={d[ids[k]]['n_res']} ctx={d[ids[k]]['n_context_atoms']}")
    nx = sum(r["n_near_native_X"] for r in ours[tag]["detail"])
    print(f"   near positions whose native residue is non-standard (X): {nx}")
    print(f"   median with no backbone-complete filter: {ours[tag]['median_nomask']:.3f}")
