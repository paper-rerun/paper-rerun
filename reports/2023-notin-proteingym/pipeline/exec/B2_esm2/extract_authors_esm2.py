# The PG_v1.3 zero_shot_substitutions_scores.zip is flat: 217 merged CSVs, one column per model (named by the config.json key).
# Keep only what the ESM2 comparison needs in authors_merged/<DMS_id>.csv
import os, zipfile
import pandas as pd

Zip = "/mnt/e/Ciencia/pipeline/2023-notin-proteingym/data/zero_shot_substitutions_scores.zip"
Out = "/mnt/e/Ciencia/pipeline/2023-notin-proteingym/exec/B2_esm2/authors_merged"
Columns = ["mutant", "DMS_score", "DMS_score_bin", "ESM2_8M", "ESM2_35M", "ESM2_150M", "ESM2_650M"]
os.makedirs(Out, exist_ok=True)
with zipfile.ZipFile(Zip) as Archive:
	Names = [Name for Name in Archive.namelist() if Name.endswith(".csv")]
	for Name in Names:
		Target = os.path.join(Out, os.path.basename(Name))
		if os.path.exists(Target):
			continue
		with Archive.open(Name) as File:
			Scores = pd.read_csv(File, usecols=Columns)
		Scores.to_csv(Target + ".tmp", index=False)
		os.replace(Target + ".tmp", Target)
print("files:", len(os.listdir(Out)))
