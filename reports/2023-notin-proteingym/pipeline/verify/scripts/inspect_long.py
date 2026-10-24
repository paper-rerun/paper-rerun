# Where do our scores and the authors' released scores disagree on the long (>1022 aa) assays? Grouped by mutated position
# Usage: inspect_long.py <data folder> <verify folder> <our folder> <our column> <authors column> <DMS_id> [<DMS_id> ...]
import sys, zipfile
import numpy as np
import pandas as pd

DataFolder, VerifyFolder, Folder, Column, AuthorsColumn = sys.argv[1:6]
with zipfile.ZipFile(f"{DataFolder}/zero_shot_substitutions_scores.zip") as Archive:
	for DmsId in sys.argv[6:]:
		with Archive.open(f"{DmsId}.csv") as File:
			Authors = pd.read_csv(File, usecols=["mutant", "DMS_score", AuthorsColumn])
		Ours = pd.read_csv(f"{VerifyFolder}/scores/{Folder}/{DmsId}.csv", usecols=["mutant", Column])
		Merged = Ours.merge(Authors, on="mutant")
		Merged["position"] = Merged["mutant"].str.split(":").str[0].str[1:-1].astype(int)
		Merged["abs_diff"] = (Merged[Column] - Merged[AuthorsColumn]).abs()
		print(DmsId, "mutants", len(Merged), "multi", int(Merged["mutant"].str.contains(":").sum()), "positions", Merged["position"].min(), "-", Merged["position"].max(), "share with diff > 0.01:", round((Merged["abs_diff"] > 0.01).mean(), 3))
		print("  pearson ours vs authors", round(np.corrcoef(Merged[Column], Merged[AuthorsColumn])[0, 1], 4))
		Bins = pd.cut(Merged["position"], bins=8)
		print(Merged.groupby(Bins, observed=True)["abs_diff"].agg(["count", "median", "max"]).round(4).to_string())
