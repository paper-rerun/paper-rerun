"""Alternative chosen after seeing data: our ESM2 per-assay Spearman, with the 5 long assays whose MSA covers
only part of target_seq re-scored on the MSA region (logs/msa_region_hypothesis.log), then the same corrected average.
Log lines without a model prefix are the first two blocks: 8M then 35M (in that order, see msa_region_hypothesis.sh).
"""
import re
import pandas as pd

W = "/mnt/e/Ciencia/meio/2023-notin-proteingym/runs"
Pattern = re.compile(r"^(?:(ESM2_\w+) )?(\S+) region=\S+ spearman_vs_authors=\S+ max_abs_diff=\S+ spearman_vs_DMS=(\S+)")
RegionValues = {}
UnlabelledOrder = ["ESM2_8M"] * 5 + ["ESM2_35M"] * 5
Unlabelled = 0
for Line in open(f"{W}/logs/msa_region_hypothesis.log"):
	Match = Pattern.match(Line.strip())
	if not Match:
		continue
	Model = Match.group(1)
	if Model is None:
		Model = UnlabelledOrder[Unlabelled]
		Unlabelled += 1
	RegionValues.setdefault(Model, {})[Match.group(2)] = float(Match.group(3))

Runs = {"ESM2_8M": 0.226, "ESM2_35M": 0.321, "ESM2_150M": 0.387, "ESM2_650M": 0.414}
for Model, Paper in Runs.items():
	if Model not in RegionValues or len(RegionValues[Model]) < 5:
		print(f"{Model}: MSA-region values missing, skipped")
		continue
	try:
		PerAssay = pd.read_csv(f"{W}/results/{Model}_per_assay.csv")
	except FileNotFoundError:
		print(f"{Model}: main run not evaluated yet, skipped")
		continue
	for DmsId, Value in RegionValues[Model].items():
		PerAssay.loc[PerAssay.DMS_id == DmsId, "spearman"] = Value
	Corrected = PerAssay.groupby(["UniProt_ID", "coarse_selection_type"])["spearman"].mean().groupby("coarse_selection_type").mean().mean()
	print(f"{Model}: corrected average with MSA-region scoring on the 5 assays = {Corrected:.4f} (paper {Paper})")
