"""Rebuild the authors' scaffold splits and print fold sizes, before and after the
SELFIES filter. Compared against the fold sizes recovered from the released
checkpoints' trainer_state.json, this says whether our split is theirs.
"""
import json
import os
import sys

os.environ.setdefault("MPLBACKEND", "Agg")

import pandas as pd

REPO = r"E:\Ciencia\noturno\2023-yuksel-selformer-cego\repo\SELFormer"
sys.path.insert(0, REPO)
import to_selfies  # noqa: E402
from prepare_finetuning_data import train_val_test_split, train_val_test_split_multilabel  # noqa: E402

BIN = {"bace": 1, "bbbp": 1, "hiv": 1}
MULTI = ["tox21", "sider"]
out = {}

for task, col in BIN.items():
    path = os.path.join(REPO, "data", "finetuning_datasets", "classification", task, task + ".csv")
    tr, va, te = train_val_test_split(path, col, scaffold_split=True)
    sizes = {}
    for name, fold in (("train", tr), ("val", va), ("test", te)):
        sm = [item[0] for item in fold.smiles()]
        # same drop rule as smiles_to_selfies, applied without pandarallel
        kept = [s for s in sm if to_selfies.to_selfies(s) != s]
        sizes[name] = {"raw": len(sm), "after_selfies_filter": len(kept)}
    out[task] = sizes
    print(task, json.dumps(sizes), flush=True)

for task in MULTI:
    path = os.path.join(REPO, "data", "finetuning_datasets", "classification", task, task + ".csv")
    tr, va, te = train_val_test_split_multilabel(path, scaffold_split=True)
    sizes = {}
    for name, fold in (("train", tr), ("val", va), ("test", te)):
        sm = [item[0] for item in fold.smiles()]
        kept = [s for s in sm if to_selfies.to_selfies(s) != s]
        sizes[name] = {"raw": len(sm), "after_selfies_filter": len(kept)}
    out[task] = sizes
    print(task, json.dumps(sizes), flush=True)

with open(r"E:\Ciencia\noturno\2023-yuksel-selformer-cego\results\split_sizes.json", "w") as fh:
    json.dump(out, fh, indent=2)
