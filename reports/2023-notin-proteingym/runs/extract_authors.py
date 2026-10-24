"""Pull mutant, DMS_score and the ESM columns out of the authors' merged per-assay score files."""
import zipfile
import pandas as pd
W = "/mnt/e/Ciencia/meio/2023-notin-proteingym"
Columns = ["mutant", "DMS_score", "ESM1b", "ESM2_8M", "ESM2_35M", "ESM2_150M", "ESM2_650M"]
import os
os.makedirs(f"{W}/sources/authors_esm_scores", exist_ok=True)
with zipfile.ZipFile(f"{W}/sources/zero_shot_substitutions_scores.zip") as Archive:
	for Name in Archive.namelist():
		if not Name.endswith(".csv"):
			continue
		with Archive.open(Name) as Handle:
			pd.read_csv(Handle, usecols=Columns)[Columns].to_csv(f"{W}/sources/authors_esm_scores/{os.path.basename(Name)}", index=False)
print("extracted", len(os.listdir(f"{W}/sources/authors_esm_scores")))
