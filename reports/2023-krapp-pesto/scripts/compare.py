# Compare our per-item AUCs with the paper claims and the authors' per-item values (claims.json intervals)
# Usage: python -I compare.py <work_dir>
import csv
import statistics
import sys

import pandas as pd

w = sys.argv[1]


def verdict(value, low, high):
	return "inside" if low <= value < high else "OUTSIDE"


# ---- MaSIF-site set (C1, C2)
ours = pd.read_csv(f"{w}/runs/out/masif_per_item.csv")
auth = pd.read_csv(f"{w}/sources/authors_cell6_pesto_auc_per_item.csv")
scored = ours[ours["masif_len_match"] == 1]
print("MaSIF set: items built and selected:", len(ours), "| with MaSIF length match (enter the median):", len(scored))
print("authors' items:", len(auth), "| authors' keys found in ours (len match):", auth["key"].isin(scored["key"]).sum())
print("our items not in authors' list:", sorted(set(ours["key"]) - set(auth["key"])))
print("authors' items missing from our median:", sorted(set(auth["key"]) - set(scored["key"])))
c1 = scored["PeSTo"].median()
c2 = scored["MaSIF-site"].median()
print(f"C1 PeSTo median ROC AUC = {c1:.4f} (paper 0.92, interval [0.915, 0.930)) -> {verdict(c1, 0.915, 0.930)}")
print(f"C2 MaSIF-site median ROC AUC = {c2:.4f} (paper 0.80, interval [0.795, 0.810)) -> {verdict(c2, 0.795, 0.810)}")
print(f"means: PeSTo {scored['PeSTo'].mean():.4f} (notebook 0.86), MaSIF-site {scored['MaSIF-site'].mean():.4f} (notebook 0.79)")
merged = auth.merge(scored, on="key", suffixes=("_authors", "_ours"))
d = (merged["PeSTo"] - merged["auc"]).abs()
print(f"per item vs authors (n={len(merged)}): |diff|<=0.0005 {int((d <= 0.0005).sum())}, <=0.001 {int((d <= 0.001).sum())}, <=0.01 {int((d <= 0.01).sum())}, max {d.max():.4f}")
for _, r in merged[d > 0.001].iterrows():
	print(f"   differs: {r['key']} authors {r['auc']:.3f} ours {r['PeSTo']:.4f}")
merged[["key", "auc", "PeSTo", "MaSIF-site", "n_res", "n_pos"]].rename(columns={"auc": "PeSTo_authors", "PeSTo": "PeSTo_ours", "MaSIF-site": "MaSIF_ours"}).to_csv(f"{w}/runs/out/masif_vs_authors.csv", index=False)

# ---- C5 from Source Data, and the same count on our values (rows with SPPIDER/PSIVER taken from Source Data by sid order is not possible, so only Source Data)
comp = list(csv.DictReader(open(f"{w}/sources/source_data_fig2b_comparison.csv")))
n_best = sum(1 for r in comp if float(r["PeSTo"]) > max(float(r["MaSIF-site"]), float(r["SPPIDER"]), float(r["PSIVER"])))
print(f"C5 Source Data rows: {len(comp)}, PeSTo strictly best of 4: {n_best}, 'best' column == PeSTo: {sum(1 for r in comp if r['best'] == 'PeSTo')} (paper 38)")
nb = list(csv.DictReader(open(f"{w}/sources/authors_cell9_table.csv")))
n_best_nb5 = sum(1 for r in nb if r["best"] == "PeSTo")
print(f"   notebook cell 9 'best' over 5 methods incl. ScanNet: PeSTo {n_best_nb5} of {len(nb)}")
n_ours = int((scored["PeSTo"] > scored["MaSIF-site"]).sum())
print(f"   ours: PeSTo > MaSIF-site on {n_ours} of {len(scored)} items")

# ---- ScanNet set (C3, C4)
sd = pd.read_csv(f"{w}/sources/source_data_fig2b_scannet.csv")
c4 = sd["ScanNet-noMSA_auc"].median()
print(f"C4 Source Data ScanNet-noMSA median = {c4:.4f} (paper 0.87, interval [0.865, 0.880)) -> {verdict(c4, 0.865, 0.880)}; Source Data PeSTo median = {sd['PeSTo_auc'].median():.4f}, ScanNet (MSA) median = {sd['ScanNet_auc'].median():.4f}")
try:
	sc = pd.read_csv(f"{w}/runs/out/scannet_per_sid.csv")
except FileNotFoundError:
	print("C3 not run yet")
	sys.exit(0)
sc = sc[sc["sid"].isin(sd["sid"])]
dup = sc["sid"].duplicated().sum()
defined = sc.dropna(subset=["PeSTo"])
c3 = defined["PeSTo"].median()
print(f"C3 sids built: {sc['sid'].nunique()} of {len(sd)}, duplicated sids: {dup}, with defined AUC: {len(defined)}")
print("   sids missing:", sorted(set(sd["sid"]) - set(sc["sid"])))
print(f"C3 PeSTo median ROC AUC = {c3:.4f} (paper 0.93, SI 0.929, interval [0.925, 0.940)) -> {verdict(c3, 0.925, 0.940)}")
m = sd.merge(defined, on="sid")
d = (m["PeSTo"] - m["PeSTo_auc"]).abs()
print(f"   per sid vs Source Data PeSTo_auc (n={len(m)}): |diff|<=0.001 {int((d <= 0.001).sum())}, <=0.01 {int((d <= 0.01).sum())}, <=0.05 {int((d <= 0.05).sum())}, max {d.max():.4f}")
print(f"   median over the same sids: ours {m['PeSTo'].median():.4f}, Source Data PeSTo {m['PeSTo_auc'].median():.4f}, Source Data ScanNet-noMSA {m['ScanNet-noMSA_auc'].median():.4f}")
m[["sid", "PeSTo_auc", "PeSTo", "ScanNet-noMSA_auc", "n_res", "n_pos"]].rename(columns={"PeSTo_auc": "PeSTo_source_data", "PeSTo": "PeSTo_ours"}).to_csv(f"{w}/runs/out/scannet_vs_source_data.csv", index=False)
