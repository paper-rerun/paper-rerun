"""Score a released SELFormer multi-label checkpoint on the scaffold test fold.

Mirrors train_classification_multilabel_model.py: same model wrapper, same split call,
same SELFIES filter, same metric. Training is removed.
"""
import argparse
import json
import os
import sys

os.environ["TOKENIZER_PARALLELISM"] = "false"
os.environ["WANDB_DISABLED"] = "true"
os.environ.setdefault("MPLBACKEND", "Agg")

import numpy as np
import pandas as pd
import torch
from sklearn.metrics import auc, precision_recall_curve, roc_auc_score

parser = argparse.ArgumentParser()
parser.add_argument("--repo", required=True)
parser.add_argument("--model", required=True)
parser.add_argument("--dataset", required=True)
parser.add_argument("--eval_batch_size", type=int, default=8)
parser.add_argument("--out", required=True)
args = parser.parse_args()

sys.path.insert(0, args.repo)
from simpletransformers.classification import MultiLabelClassificationModel  # noqa: E402
from prepare_finetuning_data import smiles_to_selfies, train_val_test_split_multilabel  # noqa: E402

if torch.cuda.is_available():
    torch.cuda.set_per_process_memory_fraction(0.5, 0)

num_labels = len(pd.read_csv(args.dataset).columns) - 1
model_args = {
    "eval_batch_size": args.eval_batch_size,
    "process_count": 1,
    "use_multiprocessing": False,
    "use_multiprocessing_for_evaluation": False,
    "silent": True,
    "output_dir": os.path.join(os.path.dirname(args.out), "st_out"),
}
model = MultiLabelClassificationModel(
    "roberta", args.model, num_labels=num_labels,
    use_cuda=torch.cuda.is_available(), args=model_args,
)

print("Using scaffold split", flush=True)
(train, val, test) = train_val_test_split_multilabel(args.dataset, scaffold_split=True)
train_smiles = [item[0] for item in train.smiles()]
test_smiles = [item[0] for item in test.smiles()]
cols = ["smiles"] + ["Feature_" + str(i) for i in range(num_labels)]
train_df = pd.DataFrame(np.column_stack([train_smiles, train.targets()]), columns=cols)
test_df = pd.DataFrame(np.column_stack([test_smiles, test.targets()]), columns=cols)
split_sizes_raw = {"train": len(train_df), "val": len(val.smiles()), "test": len(test_df)}

train_df = smiles_to_selfies(train_df)
test_df = smiles_to_selfies(test_df)
test_df.insert(
    1, "labels",
    np.array([test_df["Feature_" + str(i)].to_numpy() for i in range(len(test_df.columns[1:]))],
             dtype=np.float32).T.tolist(),
)

preds, outputs = model.predict(test_df["selfies"].tolist())

y_true = np.ravel(test_df["labels"].tolist())
y_pred = np.ravel(preds)

# Frozen metric C2
roc_frozen = roc_auc_score(y_true=y_true, y_score=y_pred)
p_c, r_c, _ = precision_recall_curve(y_true, y_pred)
prc_frozen = auc(r_c, p_c)

# Extra analysis E1 / E2: sigmoid scores
scores = 1.0 / (1.0 + np.exp(-np.asarray(outputs, dtype=np.float64)))
roc_micro_prob = roc_auc_score(y_true=y_true, y_score=np.ravel(scores))
Y = np.asarray(test_df["labels"].tolist(), dtype=int)
per_label = []
for j in range(Y.shape[1]):
    if len(np.unique(Y[:, j])) < 2:
        per_label.append(None)
    else:
        per_label.append(float(roc_auc_score(Y[:, j], scores[:, j])))
usable = [v for v in per_label if v is not None]

res = {
    "model": args.model,
    "dataset": args.dataset,
    "num_labels": num_labels,
    "split_sizes_before_selfies_filter": split_sizes_raw,
    "n_test_scored": int(len(test_df)),
    "n_test_dropped_by_selfies_filter": int(split_sizes_raw["test"] - len(test_df)),
    "roc_frozen_C2_hardlabels_micro": float(roc_frozen),
    "prc_frozen_hardlabels_micro": float(prc_frozen),
    "roc_E1_probabilities_micro": float(roc_micro_prob),
    "roc_E2_probabilities_macro": float(np.mean(usable)) if usable else None,
    "roc_E2_labels_usable": len(usable),
    "per_label_roc_probabilities": per_label,
    "accuracy_flat": float((y_true == y_pred).mean()),
    "eval_batch_size": args.eval_batch_size,
}
print(json.dumps(res, indent=2))
with open(args.out, "w") as fh:
    json.dump(res, fh, indent=2)

base = os.path.splitext(args.out)[0]
pd.DataFrame({"smiles": test_smiles}).to_csv(base + "_test_smiles.csv", index=False)
pd.DataFrame({"smiles": train_smiles}).to_csv(base + "_train_smiles.csv", index=False)
np.save(base + "_scores.npy", np.asarray(outputs))
