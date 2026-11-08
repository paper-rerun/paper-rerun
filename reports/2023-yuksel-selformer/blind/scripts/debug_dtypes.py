import os
import sys

os.environ.setdefault("MPLBACKEND", "Agg")
import numpy as np
import pandas as pd
import torch

REPO = sys.argv[1]
sys.path.insert(0, REPO)
from prepare_finetuning_data import smiles_to_selfies, train_val_test_split

path = os.path.join(REPO, "data", "finetuning_datasets", "classification", "bace", "bace.csv")
tr, va, te = train_val_test_split(path, 1, scaffold_split=True)
test_smiles = [item[0] for item in te.smiles()]
print("targets() sample:", te.targets()[:3], type(te.targets()[0]))
arr = np.column_stack([test_smiles, te.targets()])
print("column_stack dtype:", arr.dtype)
test_df = pd.DataFrame(arr, columns=["smiles", "target"])
print("df dtypes:\n", test_df.dtypes)
print("sample values:", [repr(v) for v in test_df.target.head(3)])
test_df = smiles_to_selfies(test_df)
print("after selfies, dtypes:\n", test_df.dtypes)
labels = test_df.iloc[:, 1].tolist()
print("label sample:", [repr(v) for v in labels[:3]])
t = torch.tensor(labels, dtype=torch.long)
print("torch ok:", t[:5])
test_y = pd.DataFrame(test_df.target, columns=["target"])
from sklearn.utils.multiclass import type_of_target
print("type_of_target(test_y):", type_of_target(test_y))
print("type_of_target(values):", type_of_target(test_y.values))
