"""Compare our per-mutant scores with the authors' released ones, assay by assay.

Usage: compare_authors.py <our_dir> <authors_dir> <our_column> <authors_column> <label> [out_csv]
Prints the worst agreement and how many assays fall under Spearman 0.999.
"""
import os
import sys
import numpy as np
import pandas as pd
from scipy.stats import spearmanr

OurDir, AuthorsDir, OurColumn, AuthorsColumn, Label = sys.argv[1:6]
Rows = []
for FileName in sorted(os.listdir(OurDir)):
	if not FileName.endswith(".csv"):
		continue
	AuthorsFile = AuthorsDir + os.sep + FileName
	if not os.path.exists(AuthorsFile):
		Rows.append({"DMS_id": FileName[:-4], "missing_authors_file": True})
		continue
	Ours = pd.read_csv(OurDir + os.sep + FileName, usecols=["mutant", OurColumn]).rename(columns={OurColumn: "score"})
	Theirs = pd.read_csv(AuthorsFile, usecols=["mutant", AuthorsColumn]).rename(columns={AuthorsColumn: "score"})
	Merged = Ours.merge(Theirs, on="mutant", suffixes=("_ours", "_authors"))
	Rows.append({
		"DMS_id": FileName[:-4],
		"missing_authors_file": False,
		"n_ours": len(Ours),
		"n_authors": len(Theirs),
		"n_matched": len(Merged),
		"spearman_ours_vs_authors": spearmanr(Merged["score_ours"], Merged["score_authors"])[0],
		"max_abs_diff": float(np.abs(Merged["score_ours"] - Merged["score_authors"]).max()),
	})
Table = pd.DataFrame(Rows)
Compared = Table[~Table.missing_authors_file]
print(f"{Label}: assays compared={len(Compared)} missing_authors={int(Table.missing_authors_file.sum())} "
	f"min_spearman={Compared.spearman_ours_vs_authors.min():.6f} median_spearman={Compared.spearman_ours_vs_authors.median():.6f} "
	f"below_0.999={(Compared.spearman_ours_vs_authors < 0.999).sum()} max_abs_diff={Compared.max_abs_diff.max():.4g} "
	f"row_mismatch={(Compared.n_matched != Compared.n_ours).sum()}")
Worst = Compared.sort_values("spearman_ours_vs_authors").head(6)
print(Worst[["DMS_id", "n_matched", "spearman_ours_vs_authors", "max_abs_diff"]].to_string(index=False))
if len(sys.argv) > 6:
	Table.to_csv(sys.argv[6], index=False)
