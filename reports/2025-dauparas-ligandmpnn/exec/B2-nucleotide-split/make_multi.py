"""Builds the --pdb_path_multi json for one flavor, skipping ids that already have a
stats .pt in the given out folder. The first long run was terminated two thirds of the
way through, so every run has to be resumable."""
import json
import os
import sys

ROOT = "/mnt/e/Ciencia/pipeline/2025-dauparas-ligandmpnn"
BLOCK = os.path.join(ROOT, "exec/B2-nucleotide-split")

flavor = sys.argv[1]
out_folder = sys.argv[2] if len(sys.argv) > 2 else ""
dest = sys.argv[3] if len(sys.argv) > 3 else os.path.join(BLOCK, f"pdb_multi_{flavor}.json")

ids = json.load(open(os.path.join(ROOT, "repo/training/test_nucleotide.json")))
assert len(ids) == 74

paths = {}
for pid in ids:
    if out_folder and os.path.exists(os.path.join(out_folder, "stats", pid + ".pt")):
        continue
    p = os.path.join(ROOT, "data/structures", flavor, pid + ".pdb")
    assert os.path.exists(p), p
    paths[p] = ""

json.dump(paths, open(dest, "w"), indent=1)
print(f"wrote {dest}: {len(paths)} to do, {74 - len(paths)} already done")
