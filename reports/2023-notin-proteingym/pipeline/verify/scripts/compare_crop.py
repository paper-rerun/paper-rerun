# Compare MSA-cropped-sequence scores with the authors' released scores (per mutant and per-assay Spearman)
# Usage: compare_crop.py <data folder> <crop folder> <our column> <authors column> <DMS_id ...>
import sys, zipfile
import numpy as np
import pandas as pd
DataFolder, CropFolder, Column, AuthorsColumn = sys.argv[1:5]
with zipfile.ZipFile(f"{DataFolder}/zero_shot_substitutions_scores.zip") as Archive:
	for DmsId in sys.argv[5:]:
		with Archive.open(f"{DmsId}.csv") as File:
			Authors = pd.read_csv(File, usecols=["mutant", "DMS_score", AuthorsColumn])
		Cropped = pd.read_csv(f"{CropFolder}/{DmsId}.csv", usecols=["mutant", Column])
		Merged = Cropped.merge(Authors, on="mutant")
		Difference = (Merged[Column] - Merged[AuthorsColumn]).abs()
		RankCrop = Merged[[Column, "DMS_score"]].rank().corr().iloc[0, 1]
		RankAuthors = Merged[[AuthorsColumn, "DMS_score"]].rank().corr().iloc[0, 1]
		print(DmsId, "matched", len(Merged), "max abs diff", round(Difference.max(), 5), "spearman cropped", round(RankCrop, 4), "spearman authors scores", round(RankAuthors, 4))
