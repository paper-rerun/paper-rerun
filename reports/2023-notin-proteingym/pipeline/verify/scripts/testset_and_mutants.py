# C0 test-set counts, and per-mutant agreement between our scores and the authors' released scores (zero_shot_substitutions_scores.zip)
# Usage: testset_and_mutants.py <repo> <data folder> <verify folder>
import sys, os, json, zipfile
import numpy as np
import pandas as pd

Repo, DataFolder, VerifyFolder = sys.argv[1], sys.argv[2], sys.argv[3]
Reference = pd.read_csv(f"{Repo}/reference_files/DMS_substitutions.csv")

# Test set: reference rows and the actual rows of the 217 assay files
FileRows = {}
for _, Assay in Reference.iterrows():
	Frame = pd.read_csv(f"{DataFolder}/DMS_ProteinGym_substitutions/{Assay['DMS_filename']}")
	FileRows[Assay["DMS_id"]] = len(Frame)
TestSet = {
	"assays_in_reference": int(len(Reference)),
	"unique_DMS_id": int(Reference["DMS_id"].nunique()),
	"assay_files_on_disk": int(len([Name for Name in os.listdir(f"{DataFolder}/DMS_ProteinGym_substitutions") if Name.endswith(".csv")])),
	"mutants_reference_column": int(Reference["DMS_total_number_mutants"].sum()),
	"mutants_counted_in_files": int(sum(FileRows.values())),
	"files_matching_reference_count": int(sum(FileRows[Row["DMS_id"]] == Row["DMS_total_number_mutants"] for _, Row in Reference.iterrows())),
	"unique_UniProt_ID": int(Reference["UniProt_ID"].nunique()),
	"seq_len_over_1022": int((Reference["seq_len"] > 1022).sum()),
	"coarse_selection_type": Reference["coarse_selection_type"].value_counts().sort_index().to_dict(),
}
print(json.dumps(TestSet, indent=1))
with open(f"{VerifyFolder}/testset.json", "w") as File:
	json.dump(TestSet, File, indent=1)

# Per-mutant agreement with the authors' released scores
Pairs = [("ESM1b", "esm1b_t33_650M_UR50S", "ESM1b"), ("ESM2/8M", "esm2_t6_8M_UR50D", "ESM2_8M"), ("ESM2/35M", "esm2_t12_35M_UR50D", "ESM2_35M"), ("ESM2/150M", "esm2_t30_150M_UR50D", "ESM2_150M"), ("ESM2/650M", "esm2_t33_650M_UR50D", "ESM2_650M")]
Rows = []
with zipfile.ZipFile(f"{DataFolder}/zero_shot_substitutions_scores.zip") as Archive:
	for _, Assay in Reference.iterrows():
		Available = [Pair for Pair in Pairs if os.path.exists(f"{VerifyFolder}/scores/{Pair[0]}/{Assay['DMS_id']}.csv")]
		if not Available:
			continue
		with Archive.open(f"{Assay['DMS_id']}.csv") as File:
			Authors = pd.read_csv(File, usecols=["mutant"] + [Pair[2] for Pair in Available])
		for Folder, Column, AuthorsColumn in Available:
			Ours = pd.read_csv(f"{VerifyFolder}/scores/{Folder}/{Assay['DMS_id']}.csv", usecols=["mutant", Column])
			Merged = Ours.merge(Authors[["mutant", AuthorsColumn]], on="mutant", how="outer", indicator=True)
			Both = Merged[Merged["_merge"] == "both"]
			Difference = (Both[Column] - Both[AuthorsColumn]).abs()
			Rows.append({"model": AuthorsColumn, "DMS_id": Assay["DMS_id"], "seq_len": Assay["seq_len"], "n_ours": len(Ours), "n_authors": len(Authors), "n_matched": len(Both), "max_abs_diff": float(Difference.max()), "median_abs_diff": float(Difference.median()), "pearson": float(np.corrcoef(Both[Column], Both[AuthorsColumn])[0, 1])})
Mutants = pd.DataFrame(Rows)
Mutants.to_csv(f"{VerifyFolder}/per_mutant_agreement.csv", index=False)
for Model, Group in Mutants.groupby("model", sort=False):
	print(Model, "assays", len(Group), "all mutants matched", bool((Group["n_matched"] == Group["n_ours"]).all() and (Group["n_matched"] == Group["n_authors"]).all()), "max abs diff", round(Group["max_abs_diff"].max(), 5), "min pearson", round(Group["pearson"].min(), 6), "assays with max diff > 0.01:", int((Group["max_abs_diff"] > 0.01).sum()))
	print("   worst:", Group.sort_values("max_abs_diff", ascending=False)[["DMS_id", "seq_len", "max_abs_diff", "pearson"]].head(4).round(5).values.tolist())
