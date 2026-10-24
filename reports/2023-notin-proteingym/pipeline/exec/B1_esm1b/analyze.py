# Compare our ESM-1b run with the paper and with the authors' PG_v1.3 tables
# Usage: analyze.py [ours|authors] [--no-mutants]. Inputs: performance_<tag>/ (authors' performance script on our or their scores), the authors' DMS-level CSVs in repo/benchmarks,
# and optionally the authors' per-mutant scores. Writes per_assay_<metric>_<tag>.csv, per_mutant_check.csv and results_<tag>.json
import csv, json, math, os, random, statistics, sys
from collections import defaultdict

W = "/mnt/e/Ciencia/pipeline/2023-notin-proteingym"
B = W + "/exec/B1_esm1b"
Tag = sys.argv[1] if len(sys.argv) > 1 and not sys.argv[1].startswith("--") else "ours"
Metrics = ["Spearman", "AUC", "MCC", "NDCG", "Top_recall"]
ClaimIds = {"Spearman": "C1", "AUC": "C6", "MCC": "C7", "NDCG": "C8", "Top_recall": "C9"}
Paper = {"Spearman": 0.394, "AUC": 0.719, "MCC": 0.311, "NDCG": 0.747, "Top_recall": 0.203}
Tolerance = {"Spearman": 0.014, "AUC": 0.008, "MCC": 0.012, "NDCG": 0.015, "Top_recall": 0.007}


def Mean(Values):
	return sum(Values) / len(Values)


def ReadDmsLevel(Path, Column):
	Rows = {}
	for Row in csv.DictReader(open(Path)):
		if Row["DMS ID"] in ("", "Average"):
			continue
		Uniprot = Row.get("UniProt ID", Row.get("UniProt_ID"))
		Rows[Row["DMS ID"]] = (float(Row[Column]), Row["Selection Type"], Uniprot)
	return Rows


# Units per function type: (UniProt, type) means for the code definition, single assays for the literal one
def Groups(Rows, CodeDefinition):
	if CodeDefinition:
		ByPair = defaultdict(list)
		for Value, Ftype, Uniprot in Rows.values():
			ByPair[(Ftype, Uniprot)].append(Value)
		Result = defaultdict(list)
		for (Ftype, Uniprot), Values in ByPair.items():
			Result[Ftype].append(Mean(Values))
		return Result
	Result = defaultdict(list)
	for Value, Ftype, Uniprot in Rows.values():
		Result[Ftype].append(Value)
	return Result


def Corrected(GroupsByType):
	return Mean([Mean(Values) for Values in GroupsByType.values()])


# Same scheme as the tolerance rule: 10k stratified resamples, random seed 0
def BootSe(GroupsByType, Resamples=10000, Seed=0):
	Rng = random.Random(Seed)
	Keys = sorted(GroupsByType)
	Stats = []
	for _ in range(Resamples):
		Stats.append(Mean([Mean(Rng.choices(GroupsByType[Key], k=len(GroupsByType[Key]))) for Key in Keys]))
	return statistics.stdev(Stats)


Results = {}
for Metric in Metrics:
	OursPath = f"{B}/performance_{Tag}/{Metric}/DMS_substitutions_{Metric}_DMS_level.csv"
	AuthorsPath = f"{W}/repo/benchmarks/DMS_zero_shot/substitutions/{Metric}/DMS_substitutions_{Metric}_DMS_level.csv"
	Ours = ReadDmsLevel(OursPath, "ESM-1b")
	Authors = ReadDmsLevel(AuthorsPath, "ESM-1b")
	SummaryRow = next(csv.DictReader(open(f"{B}/performance_{Tag}/{Metric}/Summary_performance_DMS_substitutions_{Metric}.csv")))
	# Per-assay comparison
	Diffs = []
	with open(f"{B}/per_assay_{Metric}_{Tag}.csv", "w", newline="") as File:
		Writer = csv.writer(File)
		Writer.writerow(["DMS_id", "Selection_Type", "UniProt_ID", "ours", "authors_PG_v1.3", "diff"])
		for DmsId in Authors:
			OurValue = Ours[DmsId][0] if DmsId in Ours else float("nan")
			Diff = OurValue - Authors[DmsId][0]
			Diffs.append((abs(Diff), DmsId, Diff))
			Writer.writerow([DmsId, Authors[DmsId][1], Authors[DmsId][2], OurValue, Authors[DmsId][0], round(Diff, 4)])
	Diffs.sort(reverse=True)
	OursCode, OursLiteral = Groups(Ours, True), Groups(Ours, False)
	AuthorsCode, AuthorsLiteral = Groups(Authors, True), Groups(Authors, False)
	Value = Corrected(OursCode)
	Results[Metric] = {
		"claim_id": ClaimIds[Metric],
		"n_assays_ours": len(Ours),
		"n_assays_authors": len(Authors),
		"ours_code_definition": round(Value, 4),
		"ours_literal_definition": round(Corrected(OursLiteral), 4),
		"ours_summary_csv": float(SummaryRow[f"Average_{Metric}"]),
		"authors_code_definition": round(Corrected(AuthorsCode), 4),
		"authors_literal_definition": round(Corrected(AuthorsLiteral), 4),
		"paper": Paper[Metric],
		"tolerance": Tolerance[Metric],
		"diff_vs_paper_code": round(Value - Paper[Metric], 4),
		"within_tolerance": abs(round(Value, 3) - Paper[Metric]) <= Tolerance[Metric] + 1e-9,
		"boot_se_ours_code": round(BootSe(OursCode), 4),
		"boot_se_ours_literal": round(BootSe(OursLiteral), 4),
		"per_function_ours_code": {Key: round(Mean(Values), 4) for Key, Values in sorted(OursCode.items())},
		"per_assay_max_abs_diff": round(Diffs[0][0], 4),
		"per_assay_n_abs_diff_gt_0.001": sum(1 for D in Diffs if D[0] > 0.0011),
		"per_assay_n_exact": sum(1 for D in Diffs if D[0] < 1e-9),
		"per_assay_largest_diffs": [(DmsId, round(Diff, 4)) for _, DmsId, Diff in Diffs[:8]],
	}

# Per-mutant check against the authors' released ESM-1b scores, when unpacked
AuthorsScores = f"{B}/authors_merged"
if Tag == "ours" and os.path.isdir(AuthorsScores) and "--no-mutants" not in sys.argv:
	import pandas as pd
	import numpy as np
	Reference = pd.read_csv(f"{W}/repo/reference_files/DMS_substitutions.csv")
	Rows = []
	for _, Ref in Reference.iterrows():
		OursFile = f"{B}/scores/ESM1b/{Ref.DMS_id}.csv"
		TheirsFile = f"{AuthorsScores}/{Ref.DMS_id}.csv"
		if not (os.path.exists(OursFile) and os.path.exists(TheirsFile)):
			Rows.append(dict(DMS_id=Ref.DMS_id, seq_len=Ref.seq_len, status="missing_ours" if not os.path.exists(OursFile) else "missing_authors"))
			continue
		OursDf = pd.read_csv(OursFile, usecols=["mutant", "esm1b_t33_650M_UR50S"])
		TheirsDf = pd.read_csv(TheirsFile, usecols=["mutant", "ESM1b"])
		Merged = OursDf.merge(TheirsDf.rename(columns={"ESM1b": "authors"}), on="mutant", how="outer")
		AbsDiff = (Merged["esm1b_t33_650M_UR50S"] - Merged["authors"]).abs()
		Rows.append(dict(DMS_id=Ref.DMS_id, seq_len=Ref.seq_len, status="ok", n_ours=len(OursDf), n_authors=len(TheirsDf), n_merged=len(Merged),
			n_unmatched=int(Merged.isna().any(axis=1).sum()), max_abs_diff=float(AbsDiff.max()), mean_abs_diff=float(AbsDiff.mean()),
			pearson=float(np.corrcoef(Merged.dropna()["esm1b_t33_650M_UR50S"], Merged.dropna()["authors"])[0, 1])))
	Check = pd.DataFrame(Rows)
	Check.to_csv(f"{B}/per_mutant_check.csv", index=False)
	Ok = Check[Check.status == "ok"]
	Long = Ok[Ok.seq_len > 1022]
	Results["per_mutant_vs_authors"] = {
		"n_assays_compared": int(len(Ok)),
		"n_assays_max_abs_diff_le_1e-3": int((Ok.max_abs_diff <= 1e-3).sum()),
		"n_assays_max_abs_diff_le_1e-2": int((Ok.max_abs_diff <= 1e-2).sum()),
		"overall_max_abs_diff": float(Ok.max_abs_diff.max()),
		"median_of_max_abs_diff": float(Ok.max_abs_diff.median()),
		"long_assays_n": int(len(Long)),
		"long_assays_max_abs_diff": float(Long.max_abs_diff.max()) if len(Long) else None,
		"short_assays_max_abs_diff": float(Ok[Ok.seq_len <= 1022].max_abs_diff.max()),
		"min_pearson": float(Ok.pearson.min()),
		"n_unmatched_mutants": int(Ok.n_unmatched.sum()),
		"worst_assays": Ok.sort_values("max_abs_diff", ascending=False)[["DMS_id", "seq_len", "max_abs_diff", "pearson"]].head(8).values.tolist(),
	}

json.dump(Results, open(f"{B}/results_{Tag}.json", "w"), indent=1)
print(json.dumps(Results, indent=1))
