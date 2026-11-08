import os, sys, json, numpy as np, pandas as pd, torch as pt
pt.set_num_threads(4)
w = os.path.abspath(sys.argv[1]); os.chdir(w + "/repo")
sp = "model/save/i_v4_1_2021-09-07_11-21"; sys.path.insert(0, sp); sys.path.insert(1, ".")
from config import config_data
from data_handler import Dataset
from src.dataset import select_by_sid, select_by_interface_types
from src.scoring import bc_scoring
def rb(fp):
    return np.array([float(l[60:66]) for l in open(fp) if l[:4]=="ATOM" and l[12:15].strip()=="CA"])
bj = json.load(open("masif-site_benchmark/masif_pred_per_res.json"))
d = Dataset(w + "/data/masif_subset.h5")
m = select_by_sid(d, list(bj)); m &= select_by_interface_types(d, config_data["l_types"], np.concatenate(config_data["r_types"]))
d.update_mask(m); d.set_types(config_data["l_types"], config_data["r_types"])
ours = pd.read_csv(w + "/runs/out/masif_per_item.csv").set_index("key")
rows = []
for i in range(len(d)):
    k = d.ukeys[i]; y = d[i][-1]; bid = k.split("/")[1] + "_" + k.split("/")[3][0]
    r = {"key": k, "PeSTo": ours.loc[k, "PeSTo"], "MaSIF-site": ours.loc[k, "MaSIF-site"]}
    for name, fp in [("SPPIDER", f"masif-site_benchmark/sppider_pred/{bid}.pdb"), ("PSIVER", f"masif-site_benchmark/psiver_pred/psiver_pdbs/{bid}.pdb")]:
        p = rb(fp); r[name] = float(bc_scoring(y[:, :1], pt.from_numpy(p).unsqueeze(1).float())[:, 0][6]) if len(p) == y.shape[0] else np.nan
    rows.append(r)
df = pd.DataFrame(rows)
print("n", len(df), "nan", df.isna().sum().to_dict())
print("medians", df[["PeSTo","MaSIF-site","SPPIDER","PSIVER"]].median().round(4).to_dict())
o = df[["MaSIF-site","SPPIDER","PSIVER"]].max(axis=1)
print("PeSTo strictly best of 4 (unrounded):", int((df.PeSTo > o).sum()))
r3 = df[["PeSTo","MaSIF-site","SPPIDER","PSIVER"]].round(3)
print("argmax of rounded (notebook tie rule):", int((np.argmax(r3.values,1)==0).sum()))
