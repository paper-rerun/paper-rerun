"""Score a released SELFormer binary-classification checkpoint on the scaffold test fold.

Mirrors train_classification_model.py: same model class, same Dataset/tokenisation,
same split call, same metric. Training is removed; we only run trainer.predict on the
test fold.
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
from torch.nn import CrossEntropyLoss
from torch.utils.data import Dataset
from transformers import BertPreTrainedModel, RobertaConfig, RobertaTokenizerFast
from transformers import Trainer, TrainingArguments
from transformers.models.roberta.modeling_roberta import RobertaClassificationHead, RobertaModel
from sklearn.metrics import auc, precision_recall_curve, roc_auc_score

parser = argparse.ArgumentParser()
parser.add_argument("--repo", required=True)
parser.add_argument("--model", required=True)
parser.add_argument("--tokenizer", required=True)
parser.add_argument("--dataset", required=True)
parser.add_argument("--target_column_id", type=int, default=1)
parser.add_argument("--eval_batch_size", type=int, default=8)
parser.add_argument("--out", required=True)
parser.add_argument("--tmp", required=True)
parser.add_argument("--fold", default="test", choices=["test", "val"],
                    help="Which fold to score. 'val' is the self-consistency check against "
                         "the released checkpoint's own trainer_state.json.")
args = parser.parse_args()

sys.path.insert(0, args.repo)
from prepare_finetuning_data import smiles_to_selfies, train_val_test_split  # noqa: E402

if torch.cuda.is_available():
    # House rule: at most half the 8 GB card
    torch.cuda.set_per_process_memory_fraction(0.5, 0)


class SELFIESTransformers_For_Classification(BertPreTrainedModel):
    def __init__(self, config):
        super(SELFIESTransformers_For_Classification, self).__init__(config)
        self.num_labels = config.num_labels
        self.roberta = RobertaModel(config)
        self.classifier = RobertaClassificationHead(config)

    def forward(self, input_ids, attention_mask, labels):
        outputs = self.roberta(input_ids, attention_mask=attention_mask)
        sequence_output = outputs[0]
        logits = self.classifier(sequence_output)
        outputs = (logits,) + outputs[2:]
        if labels is not None:
            loss_fct = CrossEntropyLoss()
            loss = loss_fct(logits.view(-1, self.num_labels), labels.view(-1))
            outputs = (loss,) + outputs
        return outputs


class SELFIESTransfomers_Dataset(Dataset):
    def __init__(self, data, tokenizer, MAX_LEN):
        text, labels = data
        self.examples = tokenizer(
            text=text, text_pair=None, truncation=True, padding="max_length",
            max_length=MAX_LEN, return_tensors="pt",
        )
        self.labels = torch.tensor(labels, dtype=torch.long)

    def __len__(self):
        return len(self.examples["input_ids"])

    def __getitem__(self, index):
        item = {key: self.examples[key][index] for key in self.examples}
        item["label"] = self.labels[index]
        return item


config = RobertaConfig.from_pretrained(args.model, num_labels=2)
model = SELFIESTransformers_For_Classification.from_pretrained(args.model, config=config)
tokenizer = RobertaTokenizerFast.from_pretrained(args.tokenizer, do_lower_case=False)

print("Using scaffold split", flush=True)
(train, val, test) = train_val_test_split(args.dataset, args.target_column_id, scaffold_split=True)
train_smiles = [item[0] for item in train.smiles()]
validation_smiles = [item[0] for item in val.smiles()]
test_smiles = [item[0] for item in test.smiles()]
train_df = pd.DataFrame(np.column_stack([train_smiles, train.targets()]), columns=["smiles", "target"])
validation_df = pd.DataFrame(np.column_stack([validation_smiles, val.targets()]), columns=["smiles", "target"])
test_df = pd.DataFrame(np.column_stack([test_smiles, test.targets()]), columns=["smiles", "target"])

split_sizes_raw = {"train": len(train_df), "val": len(validation_df), "test": len(test_df)}

if args.fold == "val":
    test_df = validation_df
    test_smiles = validation_smiles

train_df_s = smiles_to_selfies(train_df.copy())
test_df_s = smiles_to_selfies(test_df.copy())
test_y = pd.DataFrame(test_df_s.target, columns=["target"])

MAX_LEN = 128
test_examples = (test_df_s.iloc[:, 0].astype(str).tolist(), test_df_s.iloc[:, 1].tolist())
test_dataset = SELFIESTransfomers_Dataset(test_examples, tokenizer, MAX_LEN)

training_args = TrainingArguments(
    output_dir=args.tmp,
    per_device_eval_batch_size=args.eval_batch_size,
    disable_tqdm=True,
    report_to=[],
)
trainer = Trainer(model=model, args=training_args)
raw_pred, label_ids, _ = trainer.predict(test_dataset)

y_pred = np.argmax(raw_pred, axis=1)

# Frozen metric C1: the authors' line is
#   roc_auc_score(y_true=test_y, y_score=y_pred)
# On the scaffold branch test_y is an object-dtype DataFrame (np.column_stack turns the
# targets into Python objects), and sklearn 1.2.1 rejects that with
# "ValueError: unknown format is not supported". The cast to int is the minimum needed
# to get the number the line is asking for; nothing else changes.
try:
    roc_auc_score(y_true=test_y, y_score=y_pred)
    authors_line_runs = True
except Exception as exc:  # noqa: BLE001
    authors_line_runs = False
    authors_line_error = "%s: %s" % (type(exc).__name__, exc)
    print("authors' ROC line failed:", authors_line_error, flush=True)

test_y = test_y.astype(int)
roc_auc_score_result = roc_auc_score(y_true=test_y, y_score=y_pred)
p_c, r_c, _ = precision_recall_curve(test_y, y_pred)
prc = auc(r_c, p_c)

# Extra analysis E1: standard ROC AUC from probabilities
probs = torch.softmax(torch.tensor(raw_pred), dim=1).numpy()[:, 1]
roc_prob = roc_auc_score(y_true=test_y.values.astype(int).ravel(), y_score=probs)
p_c2, r_c2, _ = precision_recall_curve(test_y.values.astype(int).ravel(), probs)
prc_prob = auc(r_c2, p_c2)

y_true = test_y.values.astype(int).ravel()
res = {
    "model": args.model,
    "dataset": args.dataset,
    "target_column_id": args.target_column_id,
    "split_sizes_before_selfies_filter": split_sizes_raw,
    "n_test_scored": int(len(y_true)),
    "n_test_dropped_by_selfies_filter": int(split_sizes_raw["test"] - len(y_true)),
    "n_train_scored": int(len(train_df_s)),
    "test_positives": int(y_true.sum()),
    "authors_roc_line_runs_unpatched": authors_line_runs,
    "authors_roc_line_error": None if authors_line_runs else authors_line_error,
    "roc_frozen_C1_hardlabels": float(roc_auc_score_result),
    "prc_frozen_hardlabels": float(prc),
    "roc_E1_probabilities": float(roc_prob),
    "prc_E1_probabilities": float(prc_prob),
    "accuracy": float((y_pred == y_true).mean()),
    "eval_batch_size": args.eval_batch_size,
    "torch": torch.__version__,
    "cuda": torch.cuda.is_available(),
}
print(json.dumps(res, indent=2))
with open(args.out, "w") as fh:
    json.dump(res, fh, indent=2)

# keep the split for the identity checks (Q2)
base = os.path.splitext(args.out)[0]
pd.DataFrame({"smiles": test_smiles}).to_csv(base + "_test_smiles.csv", index=False)
pd.DataFrame({"smiles": train_smiles}).to_csv(base + "_train_smiles.csv", index=False)
np.save(base + "_raw_pred.npy", raw_pred)
