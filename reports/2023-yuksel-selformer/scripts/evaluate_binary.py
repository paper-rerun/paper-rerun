"""Score a published fine-tuned SELFormer model on the scaffold test split of a binary task.

This is the test block of the authors' train_classification_model.py, with the training
removed. The split, the SELFIES conversion, the tokenizer, MAX_LEN and the metric come from
the authors' own code: prepare_finetuning_data is imported unchanged. The only change is the
forward pass, a plain torch loop instead of transformers.Trainer, because nothing is trained
here. Padding is fixed at max_length=128, so the batch size cannot move a logit.
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
from torch.nn import CrossEntropyLoss
from sklearn.metrics import (accuracy_score, auc, f1_score, precision_recall_curve,
                             precision_score, recall_score, roc_auc_score)
from transformers import BertPreTrainedModel, RobertaConfig, RobertaTokenizerFast
from transformers.models.roberta.modeling_roberta import RobertaClassificationHead, RobertaModel

parser = argparse.ArgumentParser()
parser.add_argument("--repo", required=True, help="Path of the SELFormer checkout")
parser.add_argument("--task", required=True)
parser.add_argument("--dataset", required=True)
parser.add_argument("--model", required=True)
parser.add_argument("--tokenizer", required=True)
parser.add_argument("--target_column_id", type=int, default=1)
parser.add_argument("--split", default="test", choices=["test", "train", "val"])
parser.add_argument("--device", default="cpu")
parser.add_argument("--batch_size", type=int, default=32)
parser.add_argument("--out", required=True, help="CSV of per-molecule predictions")
args = parser.parse_args()

sys.path.insert(0, args.repo)
from prepare_finetuning_data import smiles_to_selfies, train_val_test_split  # noqa: E402


class SELFIESTransformers_For_Classification(BertPreTrainedModel):
    def __init__(self, config):
        super(SELFIESTransformers_For_Classification, self).__init__(config)
        self.num_labels = config.num_labels
        self.roberta = RobertaModel(config)
        self.classifier = RobertaClassificationHead(config)

    def forward(self, input_ids, attention_mask, labels=None):
        outputs = self.roberta(input_ids, attention_mask=attention_mask)
        logits = self.classifier(outputs[0])
        outputs = (logits,) + outputs[2:]
        if labels is not None:
            loss = CrossEntropyLoss()(logits.view(-1, self.num_labels), labels.view(-1))
            outputs = (loss,) + outputs
        return outputs


# Rebuild the authors' scaffold split
(train, val, test) = train_val_test_split(args.dataset, args.target_column_id, scaffold_split=True)
chosen = {"train": train, "val": val, "test": test}[args.split]
smiles = [item[0] for item in chosen.smiles()]
df = pd.DataFrame(np.column_stack([smiles, chosen.targets()]), columns=["smiles", "target"])
n_before = len(df)
df = smiles_to_selfies(df)
print("split={} rows_from_split={} rows_after_selfies={}".format(args.split, n_before, len(df)), flush=True)
print("split sizes train/val/test = {}/{}/{}".format(len(train.smiles()), len(val.smiles()), len(test.smiles())), flush=True)

y_true = pd.to_numeric(df["target"]).astype(int).to_numpy()
texts = df.iloc[:, 0].astype(str).tolist()

MAX_LEN = 128
tokenizer = RobertaTokenizerFast.from_pretrained(args.tokenizer, do_lower_case=False)
config = RobertaConfig.from_pretrained(args.model, num_labels=2)
model = SELFIESTransformers_For_Classification.from_pretrained(args.model, config=config)
model.eval()
if args.device.startswith("cuda"):
    # Half of the 8 GB card at most: this machine is in use while we run
    torch.cuda.set_per_process_memory_fraction(0.5)
model.to(args.device)

enc = tokenizer(text=texts, text_pair=None, truncation=True, padding="max_length",
                max_length=MAX_LEN, return_tensors="pt")
logits = []
with torch.no_grad():
    for i in range(0, len(texts), args.batch_size):
        out = model(input_ids=enc["input_ids"][i:i + args.batch_size].to(args.device),
                    attention_mask=enc["attention_mask"][i:i + args.batch_size].to(args.device))
        logits.append(out[0].float().cpu().numpy())
logits = np.concatenate(logits, axis=0)

y_pred = np.argmax(logits, axis=1).astype(int)
prob1 = torch.softmax(torch.tensor(logits), dim=1).numpy()[:, 1]

# The authors' metric: ROC AUC of the hard 0/1 prediction
roc_auc_hard = roc_auc_score(y_true=y_true, y_score=y_pred)
p_curve, r_curve, _ = precision_recall_curve(y_true, y_pred)
prc_auc_hard = auc(r_curve, p_curve)
# The standard metric, for reference only
roc_auc_prob = roc_auc_score(y_true=y_true, y_score=prob1)

res = {
    "task": args.task, "split": args.split, "device": args.device,
    "n_from_split": int(n_before), "n_scored": int(len(y_true)),
    "n_positive": int(y_true.sum()),
    "roc_auc_hard_pred": float(roc_auc_hard),
    "prc_auc_hard_pred": float(prc_auc_hard),
    "roc_auc_probability": float(roc_auc_prob),
    "accuracy": float(accuracy_score(y_true, y_pred)),
    "precision": float(precision_score(y_true, y_pred, zero_division=0)),
    "recall": float(recall_score(y_true, y_pred, zero_division=0)),
    "f1": float(f1_score(y_true, y_pred, zero_division=0)),
    "split_sizes": [len(train.smiles()), len(val.smiles()), len(test.smiles())],
}
print(json.dumps(res, indent=1), flush=True)

pd.DataFrame({"selfies": texts, "target": y_true, "pred": y_pred,
              "logit0": logits[:, 0], "logit1": logits[:, 1], "prob1": prob1}).to_csv(args.out, index=False)
with open(args.out.replace(".csv", ".json"), "w") as fh:
    json.dump(res, fh, indent=1)
