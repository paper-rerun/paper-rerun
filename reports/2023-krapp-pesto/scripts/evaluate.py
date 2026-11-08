# Score PeSTo i_v4_1 on a built h5, following interface_ppi_benchmark.ipynb cells 2-7 (device cpu)
# Usage: python evaluate.py <repo_dir> <dataset.h5> <masif|scannet> <out.csv> [scannet_source_data.csv]
import csv
import json
import os
import sys

import numpy as np
import pandas as pd
import torch as pt

repo_dir, h5_path, mode, out_path = sys.argv[1:5]
os.chdir(repo_dir)
save_path = "model/save/i_v4_1_2021-09-07_11-21"
sys.path.insert(0, save_path)
sys.path.insert(1, ".")
from config import config_model, config_data
from data_handler import Dataset
from model import Model
from src.dataset import collate_batch_features, select_by_sid, select_by_interface_types
from src.scoring import bc_scoring

pt.set_num_threads(int(os.environ.get("PESTO_THREADS", "6")))
device = pt.device("cpu")

# Create model and reload the checkpoint the notebook uses
model = Model(config_model)
model.load_state_dict(pt.load(os.path.join(save_path, "model_ckpt.pt"), map_location=pt.device("cpu")))
model = model.eval().to(device)

bench_pred_dict = json.load(open("masif-site_benchmark/masif_pred_per_res.json", "r"))
if mode == "masif":
	sids = list(bench_pred_dict)
else:
	sids = [r["sid"] for r in csv.DictReader(open(sys.argv[5]))]

# Same selection as notebook cell 5
dataset = Dataset(h5_path)
m = select_by_sid(dataset, sids)
m &= select_by_interface_types(dataset, config_data["l_types"], np.concatenate(config_data["r_types"]))
dataset.update_mask(m)
dataset.set_types(config_data["l_types"], config_data["r_types"])
print("items after selection:", len(dataset), flush=True)

rows = []
with pt.no_grad():
	for i in range(len(dataset)):
		key = dataset.ukeys[i]
		parts = key.split("/")
		sid = parts[1] + "_" + parts[3].split(":")[0]

		# ScanNet set: biounit 1, model copy 0 only (fixed in claims.json)
		if mode == "scannet" and not (parts[2] == "1" and parts[3].endswith(":0")):
			continue

		X, ids_topk, q, M, y = dataset[i]
		X, ids_topk, q, M = collate_batch_features([[X, ids_topk, q, M]])
		z = model(X.to(device), ids_topk.to(device), q.to(device), M.float().to(device))
		p = pt.sigmoid(z)
		auc = float(bc_scoring(y.to(device), p)[:, 0][6].numpy())

		row = {"key": key, "sid": sid, "n_res": int(y.shape[0]), "n_pos": int(y[:, 0].sum()), "PeSTo": auc, "MaSIF-site": np.nan, "masif_len_match": ""}
		if mode == "masif":
			match = y.shape[0] == len(bench_pred_dict[sid])
			row["masif_len_match"] = int(match)
			if match:
				p_b0 = pt.from_numpy(np.array(bench_pred_dict[sid])).unsqueeze(1).float()
				row["MaSIF-site"] = float(bc_scoring(y[:, :1], p_b0)[:, 0][6].numpy())
		rows.append(row)
		print(f"{key} n_res={row['n_res']} auc={auc:.3f} masif={row['MaSIF-site']:.3f}", flush=True)

df = pd.DataFrame(rows)
df.to_csv(out_path, index=False)
print("rows:", len(df))
