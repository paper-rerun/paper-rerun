# Extra (not a recomputation): 217-assay ESM2 650M corrected average under the released script, using
# our values for the 54 sampled assays + the 3 other partial-MSA assays, and the authors' per-assay values for the other 160
# (those match our runs to 3 decimals for every assay with a full MSA in 8M, 35M, 150M and the 650M sample)
# Usage: impute_650M.py <repo> <verify folder>
import sys, os
import pandas as pd
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from metrics import SpearmanFromRanks, CorrectedAverageCode, CorrectedAverageLiteral

Repo, VerifyFolder = sys.argv[1], sys.argv[2]
Reference = pd.read_csv(f"{Repo}/reference_files/DMS_substitutions.csv")
Authors = pd.read_csv(f"{Repo}/benchmarks/DMS_zero_shot/substitutions/Spearman/DMS_substitutions_Spearman_DMS_level.csv").set_index("DMS ID")["ESM2 (650M)"]
Rows = []
for _, Assay in Reference.iterrows():
	Value = float(Authors[Assay["DMS_id"]])
	Source = "authors"
	for Folder in ["scores/ESM2/650M", "extra/full_650M_partialmsa"]:
		Path = f"{VerifyFolder}/{Folder}/{Assay['DMS_id']}.csv"
		if os.path.exists(Path):
			Frame = pd.read_csv(Path)
			Value = SpearmanFromRanks(Frame["DMS_score"].values, Frame["esm2_t33_650M_UR50D"].values)
			Source = Folder
	Rows.append({"DMS_id": Assay["DMS_id"], "UniProt_ID": Assay["UniProt_ID"], "Selection Type": Assay["coarse_selection_type"], "value": Value, "source": Source})
Table = pd.DataFrame(Rows)
print(Table["source"].value_counts().to_dict())
print("650M imputed, code", round(CorrectedAverageCode(Table), 4), "literal", round(CorrectedAverageLiteral(Table), 4))
