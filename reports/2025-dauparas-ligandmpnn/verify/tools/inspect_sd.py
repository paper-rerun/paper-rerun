"""Look at what the authors' Source Data for Fig. 2 actually carries.

Used only to fix the row order and to see whether anything in there (other than
recovery itself) can settle the asymmetric-unit vs biounit-1 question before the
run. Reads nothing we produced.
"""

import json
import os

import numpy as np

SD = "E:/Ciencia/pipeline/2025-dauparas-ligandmpnn/sources/sd/x/s2"
REPO_LISTS = "E:/Ciencia/pipeline/2025-dauparas-ligandmpnn/repo/training"

SPLITS = [
    ("small_molecule", "fig_2_1", "test_small_molecule.json", 317),
    ("nucleotide", "fig_2_2", "test_nucleotide.json", 74),
    ("metal", "fig_2_3", "test_metal.json", 83),
]

for split, stem, listname, n in SPLITS:
    print("=" * 70)
    print(split, "expected n =", n)
    ids = json.load(open(os.path.join(REPO_LISTS, listname)))
    print("  repo list:", len(ids), "first:", ids[:3])

    for suffix in ("_2.npz", "_3.npz"):
        path = os.path.join(SD, stem + suffix)
        if not os.path.exists(path):
            continue
        d = np.load(path, allow_pickle=True)
        print("  --", stem + suffix)
        for k in d.files:
            a = d[k]
            head = str(a.ravel()[:3])[:90] if a.size else ""
            print("      %-12s %-14s %-10s %s" % (k, a.shape, a.dtype, head))

    # row order check against the repo list
    d = np.load(os.path.join(SD, stem + "_2.npz"), allow_pickle=True)
    if "names" in d.files:
        names = [str(x) for x in d["names"]]
        bare = [x.split("_")[0].replace(".pdb", "") for x in names]
        print("  names[:3]:", names[:3])
        print("  same order as repo list:", bare == list(ids))
        print("  same set            :", sorted(bare) == sorted(ids))

    csv = os.path.join(SD, stem + "_1.csv")
    with open(csv) as fh:
        lines = fh.read().strip().split("\n")
    print("  csv header:", lines[0], "| rows:", len(lines) - 1)
