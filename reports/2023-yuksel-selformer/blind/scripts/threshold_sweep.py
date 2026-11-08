"""Extra analysis: does any sigmoid threshold on the multi-label heads reproduce the
paper's Tox21 (0.653) and SIDER (0.745) numbers under the frozen hard-label metric?
Uses the sigmoid scores saved by eval_multilabel.py plus the labels rebuilt the same way.
"""
import json
import os
import sys

os.environ.setdefault("MPLBACKEND", "Agg")
import numpy as np
import pandas as pd
from sklearn.metrics import roc_auc_score

REPO = sys.argv[1]
RES = sys.argv[2]
sys.path.insert(0, REPO)
from prepare_finetuning_data import smiles_to_selfies, train_val_test_split_multilabel

PAPER = {"tox21": 0.653, "sider": 0.745}
out = {}
for task, paper in PAPER.items():
    path = os.path.join(REPO, "data", "finetuning_datasets", "classification", task, task + ".csv")
    num_labels = len(pd.read_csv(path).columns) - 1
    _, _, test = train_val_test_split_multilabel(path, scaffold_split=True)
    test_smiles = [item[0] for item in test.smiles()]
    cols = ["smiles"] + ["Feature_" + str(i) for i in range(num_labels)]
    test_df = pd.DataFrame(np.column_stack([test_smiles, test.targets()]), columns=cols)
    test_df = smiles_to_selfies(test_df)
    Y = np.array([test_df["Feature_" + str(i)].to_numpy() for i in range(num_labels)],
                 dtype=np.float32).T
    # simpletransformers' second return value is already sigmoid(logits), so no sigmoid here
    scores = np.load(os.path.join(RES, task + "_scores.npy")).astype(np.float64)
    y_true = Y.ravel()
    rows = []
    for th in np.arange(0.05, 0.96, 0.05):
        y_pred = (scores >= th).astype(int).ravel()
        rows.append((round(float(th), 2), float(roc_auc_score(y_true, y_pred))))
    best = min(rows, key=lambda r: abs(r[1] - paper))
    out[task] = {"paper": paper, "sweep": rows, "closest": best}
    print(task, "paper", paper, "closest", best)
    for th, v in rows:
        print("   th=%.2f roc=%.4f" % (th, v))

with open(os.path.join(RES, "threshold_sweep.json"), "w") as fh:
    json.dump(out, fh, indent=2)
