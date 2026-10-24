# Compare our ESM2 runs with the paper and with the authors' PG_v1.3 tables, one size at a time
# Usage: analyze.py <size>... Inputs: performance_<size>/ (authors' performance script on our scores), performance_authors/ (same script on the
# authors' released per-mutant scores), the authors' DMS-level CSV in repo/benchmarks, authors_merged/ (their per-mutant scores) and scores/ESM2/<size>/ (ours)
# Writes per_assay_Spearman_<size>.csv, per_mutant_check_<size>.csv and results_<size>.json
import csv, json, os, random, statistics, sys
from collections import defaultdict
import numpy as np
import pandas as pd

W = "/mnt/e/Ciencia/pipeline/2023-notin-proteingym"
B = W + "/exec/B2_esm2"
ClaimIds = {"8M": "C2", "35M": "C3", "150M": "C4", "650M": "C5"}
Paper = {"8M": 0.226, "35M": 0.321, "150M": 0.387, "650M": 0.414}
Tolerance = {"8M": 0.016, "35M": 0.018, "150M": 0.017, "650M": 0.017}
Checkpoint = {"8M": "esm2_t6_8M_UR50D", "35M": "esm2_t12_35M_UR50D", "150M": "esm2_t30_150M_UR50D", "650M": "esm2_t33_650M_UR50D"}


def Mean(Values):
	return sum(Values) / len(Values)


def ReadDmsLevel(Path, Column):
	Rows = {}
	for Row in csv.DictReader(open(Path)):
		if Row["DMS ID"] in ("", "Average"):
			continue
		Rows[Row["DMS ID"]] = (float(Row[Column]), Row["Selection Type"], Row.get("UniProt ID", Row.get("UniProt_ID")))
	return Rows


# Units per function type: (UniProt, type) means for the code definition, single assays for the literal one
def Groups(Rows, CodeDefinition):
	Result = defaultdict(list)
	if CodeDefinition:
		ByPair = defaultdict(list)
		for Value, Ftype, Uniprot in Rows.values():
			ByPair[(Ftype, Uniprot)].append(Value)
		for (Ftype, Uniprot), Values in ByPair.items():
			Result[Ftype].append(Mean(Values))
		return Result
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


Reference = pd.read_csv(f"{W}/repo/reference_files/DMS_substitutions.csv").set_index("DMS_id")
for Size in sys.argv[1:]:
	Display = f"ESM2 ({Size})"
	Ours = ReadDmsLevel(f"{B}/performance_{Size}/Spearman/DMS_substitutions_Spearman_DMS_level.csv", Display)
	AuthorsAll = ReadDmsLevel(f"{W}/repo/benchmarks/DMS_zero_shot/substitutions/Spearman/DMS_substitutions_Spearman_DMS_level.csv", Display)
	AuthorsZip = ReadDmsLevel(f"{B}/performance_authors/Spearman/DMS_substitutions_Spearman_DMS_level.csv", Display)
	Authors = {DmsId: AuthorsAll[DmsId] for DmsId in Ours}
	# The summary CSV is missing when the performance script stopped on a subset (see post.sh)
	SummaryPath = f"{B}/performance_{Size}/Spearman/Summary_performance_DMS_substitutions_Spearman.csv"
	SummaryRow = next(csv.DictReader(open(SummaryPath))) if os.path.exists(SummaryPath) else {"Average_Spearman": "nan"}

	# Per-assay comparison on the assays we scored
	Diffs = []
	with open(f"{B}/per_assay_Spearman_{Size}.csv", "w", newline="") as File:
		Writer = csv.writer(File)
		Writer.writerow(["DMS_id", "Selection_Type", "UniProt_ID", "seq_len", "ours", "authors_PG_v1.3_csv", "authors_zip_rescored", "diff_vs_csv"])
		for DmsId in sorted(Ours):
			Diff = Ours[DmsId][0] - AuthorsAll[DmsId][0]
			Diffs.append((abs(Diff), DmsId, Diff))
			Writer.writerow([DmsId, AuthorsAll[DmsId][1], AuthorsAll[DmsId][2], int(Reference.loc[DmsId, "seq_len"]), round(Ours[DmsId][0], 6),
				AuthorsAll[DmsId][0], round(AuthorsZip[DmsId][0], 6), round(Diff, 6)])
	Diffs.sort(reverse=True)
	OursCode, OursLiteral = Groups(Ours, True), Groups(Ours, False)
	Value = Corrected(OursCode)
	Result = {
		"claim_id": ClaimIds[Size],
		"checkpoint": Checkpoint[Size],
		"n_assays_ours": len(Ours),
		"full_217": len(Ours) == 217,
		"ours_code_definition": round(Value, 4),
		"ours_literal_definition": round(Corrected(OursLiteral), 4),
		"ours_summary_csv": float(SummaryRow["Average_Spearman"]),
		"authors_same_assays_code_definition": round(Corrected(Groups(Authors, True)), 4),
		"authors_same_assays_literal_definition": round(Corrected(Groups(Authors, False)), 4),
		"authors_all_217_code_definition": round(Corrected(Groups(AuthorsAll, True)), 4),
		"authors_all_217_literal_definition": round(Corrected(Groups(AuthorsAll, False)), 4),
		"paper": Paper[Size],
		"tolerance": Tolerance[Size],
		"diff_vs_paper_code": round(Value - Paper[Size], 4),
		"within_tolerance_vs_paper": abs(round(Value, 3) - Paper[Size]) <= Tolerance[Size] + 1e-9,
		"boot_se_ours_code": round(BootSe(OursCode), 4),
		"boot_se_ours_literal": round(BootSe(OursLiteral), 4),
		"per_function_ours_code": {Key: round(Mean(Values), 4) for Key, Values in sorted(OursCode.items())},
		"n_function_types_present": len(OursCode),
		"per_assay_max_abs_diff_vs_csv": round(Diffs[0][0], 6),
		"per_assay_n_abs_diff_gt_0.001": sum(1 for D in Diffs if D[0] > 0.0011),
		"per_assay_mean_diff_vs_csv": round(Mean([D[2] for D in Diffs]), 6),
		"per_assay_largest_diffs": [(DmsId, round(Diff, 4)) for _, DmsId, Diff in Diffs[:8]],
		"authors_zip_vs_csv_max_abs_diff_all_217": round(max(abs(AuthorsZip[DmsId][0] - AuthorsAll[DmsId][0]) for DmsId in AuthorsAll), 6),
	}

	# Per-mutant check against the authors' released scores for this size
	Rows = []
	for DmsId in sorted(Ours):
		OursDf = pd.read_csv(f"{B}/scores/ESM2/{Size}/{DmsId}.csv", usecols=["mutant", Checkpoint[Size]])
		TheirsDf = pd.read_csv(f"{B}/authors_merged/{DmsId}.csv", usecols=["mutant", f"ESM2_{Size}"])
		Merged = OursDf.merge(TheirsDf.rename(columns={f"ESM2_{Size}": "authors"}), on="mutant", how="outer")
		AbsDiff = (Merged[Checkpoint[Size]] - Merged["authors"]).abs()
		Both = Merged.dropna()
		Rows.append(dict(DMS_id=DmsId, seq_len=int(Reference.loc[DmsId, "seq_len"]), n_ours=len(OursDf), n_authors=len(TheirsDf),
			n_unmatched=int(Merged.isna().any(axis=1).sum()), max_abs_diff=float(AbsDiff.max()), mean_abs_diff=float(AbsDiff.mean()),
			pearson=float(np.corrcoef(Both[Checkpoint[Size]], Both["authors"])[0, 1])))
	Check = pd.DataFrame(Rows)
	Check.to_csv(f"{B}/per_mutant_check_{Size}.csv", index=False)
	Long = Check[Check.seq_len > 1022]
	Result["per_mutant_vs_authors"] = {
		"n_assays_compared": int(len(Check)),
		"n_assays_max_abs_diff_le_1e-3": int((Check.max_abs_diff <= 1e-3).sum()),
		"n_assays_max_abs_diff_le_1e-2": int((Check.max_abs_diff <= 1e-2).sum()),
		"overall_max_abs_diff": float(Check.max_abs_diff.max()),
		"median_of_max_abs_diff": float(Check.max_abs_diff.median()),
		"long_assays_n": int(len(Long)),
		"long_assays_max_abs_diff": float(Long.max_abs_diff.max()) if len(Long) else None,
		"short_assays_max_abs_diff": float(Check[Check.seq_len <= 1022].max_abs_diff.max()),
		"min_pearson": float(Check.pearson.min()),
		"n_unmatched_mutants": int(Check.n_unmatched.sum()),
		"worst_assays": Check.sort_values("max_abs_diff", ascending=False)[["DMS_id", "seq_len", "max_abs_diff", "pearson"]].head(8).values.tolist(),
	}
	json.dump(Result, open(f"{B}/results_{Size}.json", "w"), indent=1)
	print(json.dumps(Result, indent=1))
