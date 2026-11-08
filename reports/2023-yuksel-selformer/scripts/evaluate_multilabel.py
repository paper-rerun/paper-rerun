"""Score a published fine-tuned SELFormer model on the scaffold test split of a multi-label task.

This is the test block of the authors' train_classification_multilabel_model.py with the
training removed: same split (prepare_finetuning_data, imported unchanged), same SELFIES
conversion, same simpletransformers MultiLabelClassificationModel, and the same metric, which
is roc_auc_score over the flattened label matrix against the flattened 0/1 predictions.
"""
import argparse
import json
import os
import sys

os.environ["TOKENIZERS_PARALLELISM"] = "false"
os.environ["WANDB_DISABLED"] = "true"

import numpy as np
import pandas as pd
import torch
from simpletransformers.classification import MultiLabelClassificationModel
from sklearn.metrics import (accuracy_score, auc, f1_score, precision_recall_curve,
                             precision_score, recall_score, roc_auc_score)

parser = argparse.ArgumentParser()
parser.add_argument("--repo", required=True)
parser.add_argument("--task", required=True)
parser.add_argument("--dataset", required=True)
parser.add_argument("--model", required=True)
parser.add_argument("--split", default="test", choices=["test", "train", "val"])
parser.add_argument("--use_cuda", type=int, default=0)
parser.add_argument("--out", required=True)
args = parser.parse_args()

sys.path.insert(0, args.repo)
from prepare_finetuning_data import smiles_to_selfies, train_val_test_split_multilabel  # noqa: E402

num_labels = len(pd.read_csv(args.dataset).columns) - 1
(train, val, test) = train_val_test_split_multilabel(args.dataset, scaffold_split=True)
chosen = {"train": train, "val": val, "test": test}[args.split]
smiles = [item[0] for item in chosen.smiles()]
cols = ["smiles"] + ["Feature_" + str(i) for i in range(len(chosen.targets()[0]))]
df = pd.DataFrame(np.column_stack([smiles, chosen.targets()]), columns=cols)
n_before = len(df)
df = smiles_to_selfies(df)
df.insert(1, "labels", np.array([df["Feature_" + str(i)].to_numpy() for i in range(len(df.columns[1:]))],
                                dtype=np.float32).T.tolist())
print("task={} num_labels={} rows_from_split={} rows_after_selfies={}".format(
    args.task, num_labels, n_before, len(df)), flush=True)
print("split sizes train/val/test = {}/{}/{}".format(len(train.smiles()), len(val.smiles()), len(test.smiles())), flush=True)

model_args = {"process_count": 1, "use_multiprocessing": False, "use_multiprocessing_for_evaluation": False,
              "silent": True, "eval_batch_size": 32}
model = MultiLabelClassificationModel("roberta", args.model, num_labels=num_labels,
                                      use_cuda=bool(args.use_cuda), args=model_args)
preds, outputs = model.predict(df["selfies"].tolist())

y_true = np.ravel(df["labels"].tolist()).astype(int)
y_pred = np.ravel(preds).astype(int)
y_prob = np.ravel(np.asarray(outputs, dtype=float))

roc_auc_hard = roc_auc_score(y_true=y_true, y_score=y_pred)
p_curve, r_curve, _ = precision_recall_curve(y_true, y_pred)
res = {
    "task": args.task, "split": args.split, "num_labels": num_labels,
    "device": "cuda" if args.use_cuda else "cpu",
    "n_from_split": int(n_before), "n_scored": int(len(df)),
    "n_label_cells": int(len(y_true)), "n_positive_cells": int(y_true.sum()),
    "roc_auc_hard_pred": float(roc_auc_hard),
    "prc_auc_hard_pred": float(auc(r_curve, p_curve)),
    "roc_auc_probability": float(roc_auc_score(y_true=y_true, y_score=y_prob)),
    "accuracy": float(accuracy_score(y_true, y_pred)),
    "precision": float(precision_score(y_true, y_pred, zero_division=0)),
    "recall": float(recall_score(y_true, y_pred, zero_division=0)),
    "f1": float(f1_score(y_true, y_pred, zero_division=0)),
    "split_sizes": [len(train.smiles()), len(val.smiles()), len(test.smiles())],
}
print(json.dumps(res, indent=1), flush=True)

flat = pd.DataFrame({"selfies": np.repeat(df["selfies"].to_numpy(), num_labels),
                     "label_index": np.tile(np.arange(num_labels), len(df)),
                     "target": y_true, "pred": y_pred, "prob": y_prob})
flat.to_csv(args.out, index=False)
with open(args.out.replace(".csv", ".json"), "w") as fh:
    json.dump(res, fh, indent=1)
