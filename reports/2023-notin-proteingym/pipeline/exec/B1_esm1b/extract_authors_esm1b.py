# The PG_v1.3 zero_shot_substitutions_scores.zip is flat: 217 merged CSVs, one column per model.
# Keep only what the ESM-1b comparison needs (mutant, DMS_score, DMS_score_bin, ESM1b) in authors_merged/<DMS_id>.csv
import os, sys, zipfile
import pandas as pd

Zip = "/mnt/e/Ciencia/pipeline/2023-notin-proteingym/data/zero_shot_substitutions_scores.zip"
Out = "/mnt/e/Ciencia/pipeline/2023-notin-proteingym/exec/B1_esm1b/authors_merged"
os.makedirs(Out, exist_ok=True)
with zipfile.ZipFile(Zip) as Archive:
	Names = [Name for Name in Archive.namelist() if Name.endswith(".csv")]
	for Name in Names:
		Target = os.path.join(Out, os.path.basename(Name))
		if os.path.exists(Target):
			continue
		with Archive.open(Name) as File:
			Scores = pd.read_csv(File, usecols=["mutant", "DMS_score", "DMS_score_bin", "ESM1b"])
		Scores.to_csv(Target + ".tmp", index=False)
		os.replace(Target + ".tmp", Target)
print("files:", len(os.listdir(Out)))
