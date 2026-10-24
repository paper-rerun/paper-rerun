# Extra analysis: per-assay Spearman with the 5 partial-MSA assays scored on the MSA-cropped sequence, and the corrected averages that result
# Usage: crop_aggregate.py <verify folder>
import sys, os
import pandas as pd
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from metrics import SpearmanFromRanks, CorrectedAverageCode, CorrectedAverageLiteral

VerifyFolder = sys.argv[1]
PerAssay = pd.read_csv(f"{VerifyFolder}/per_assay_metrics.csv")
Spearman = PerAssay[(PerAssay["metric"] == "Spearman") & PerAssay["model"].str.startswith("ESM2")].copy()
Columns = {"ESM2 (8M)": ("8M", "esm2_t6_8M_UR50D"), "ESM2 (35M)": ("35M", "esm2_t12_35M_UR50D"), "ESM2 (150M)": ("150M", "esm2_t30_150M_UR50D"), "ESM2 (650M)": ("650M", "esm2_t33_650M_UR50D")}
for Model, Group in Spearman.groupby("model", sort=False):
	Size, Column = Columns[Model]
	Group = Group.copy()
	Replaced = []
	for Index, Row in Group.iterrows():
		CropPath = f"{VerifyFolder}/extra/crop_{Size}/{Row['DMS_id']}.csv"
		if os.path.exists(CropPath):
			Frame = pd.read_csv(CropPath)
			Group.loc[Index, "value"] = SpearmanFromRanks(Frame["DMS_score"].values, Frame[Column].values)
			Replaced.append(Row["DMS_id"])
	Difference = (Group["value"] - Group["authors"]).abs()
	print(Model, "assays", len(Group), "replaced by cropped run", len(Replaced), "code", round(CorrectedAverageCode(Group), 4), "literal", round(CorrectedAverageLiteral(Group), 4), "authors same assays code", round(CorrectedAverageCode(Group.assign(value=Group["authors"])), 4), "max abs diff vs authors", round(Difference.max(), 4), "assays > 0.0015:", int((Difference > 0.0015).sum()))
