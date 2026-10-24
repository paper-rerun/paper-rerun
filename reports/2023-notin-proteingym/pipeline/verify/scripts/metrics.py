# Per-assay metrics and corrected averages, written from the definitions (no scipy/sklearn metric calls).
# Usage: metrics.py <repo> <verify folder>     or     metrics.py --selftest
import sys, os, json
import numpy as np
import pandas as pd

def AverageRanks(Values):
	# Ranks 1..n, ties get the mean of their positions
	return pd.Series(Values).rank(method="average").values

def SpearmanFromRanks(First, Second):
	FirstRanks = AverageRanks(First)
	SecondRanks = AverageRanks(Second)
	FirstCentered = FirstRanks - FirstRanks.mean()
	SecondCentered = SecondRanks - SecondRanks.mean()
	return float((FirstCentered * SecondCentered).sum() / np.sqrt((FirstCentered ** 2).sum() * (SecondCentered ** 2).sum()))

def AreaUnderRoc(Labels, Scores):
	# Mann-Whitney U over n_pos * n_neg, ties count half
	Labels = np.asarray(Labels).astype(int)
	Ranks = AverageRanks(Scores)
	PositiveCount = Labels.sum()
	NegativeCount = len(Labels) - PositiveCount
	if PositiveCount == 0 or NegativeCount == 0:
		return np.nan
	return float((Ranks[Labels == 1].sum() - PositiveCount * (PositiveCount + 1) / 2) / (PositiveCount * NegativeCount))

def MatthewsCorrelation(Labels, Predictions):
	Labels = np.asarray(Labels).astype(int)
	Predictions = np.asarray(Predictions).astype(int)
	TruePositive = float(((Labels == 1) & (Predictions == 1)).sum())
	TrueNegative = float(((Labels == 0) & (Predictions == 0)).sum())
	FalsePositive = float(((Labels == 0) & (Predictions == 1)).sum())
	FalseNegative = float(((Labels == 1) & (Predictions == 0)).sum())
	Denominator = np.sqrt((TruePositive + FalsePositive) * (TruePositive + FalseNegative) * (TrueNegative + FalsePositive) * (TrueNegative + FalseNegative))
	# Usual convention when a row or column of the confusion table is empty
	if Denominator == 0:
		return 0.0
	return float((TruePositive * TrueNegative - FalsePositive * FalseNegative) / Denominator)

def MccAtModelMedian(Labels, Scores):
	Scores = np.asarray(Scores, dtype=float)
	return MatthewsCorrelation(Labels, (Scores >= np.median(Scores)).astype(int))

def NdcgTopTenPercent(TrueScores, ModelScores):
	# Gains = min-max scaled DMS score, cutoff k = floor(10% of n), log2 discount, rank 1 = highest model score
	TrueScores = np.asarray(TrueScores, dtype=float)
	ModelScores = np.asarray(ModelScores, dtype=float)
	Cutoff = int(np.floor(len(TrueScores) * 0.1))
	Gains = (TrueScores - TrueScores.min()) / (TrueScores.max() - TrueScores.min())
	Discounts = 1.0 / np.log2(np.arange(1, Cutoff + 1) + 1)
	ModelOrder = np.argsort(-ModelScores, kind="mergesort")[:Cutoff]
	IdealOrder = np.argsort(-Gains, kind="mergesort")[:Cutoff]
	Ideal = (Gains[IdealOrder] * Discounts).sum()
	if Ideal == 0:
		return 0.0
	return float((Gains[ModelOrder] * Discounts).sum() / Ideal)

def TopTenPercentRecall(TrueScores, ModelScores):
	TrueScores = np.asarray(TrueScores, dtype=float)
	ModelScores = np.asarray(ModelScores, dtype=float)
	TopTrue = TrueScores >= np.percentile(TrueScores, 90)
	TopModel = ModelScores >= np.percentile(ModelScores, 90)
	if TopTrue.sum() == 0:
		return 0.0
	return float((TopTrue & TopModel).sum() / TopTrue.sum())

def CorrectedAverageCode(PerAssay):
	# Protein-function pairs first, then each function type, then the plain mean of the 5 types
	PairMeans = PerAssay.groupby(["UniProt_ID", "Selection Type"])["value"].mean().reset_index()
	return float(PairMeans.groupby("Selection Type")["value"].mean().mean())

def CorrectedAverageLiteral(PerAssay):
	return float(PerAssay.groupby("Selection Type")["value"].mean().mean())

def SelfTest():
	# Checks the hand-written metrics against scipy/sklearn on random data with ties
	from scipy.stats import spearmanr
	from sklearn.metrics import roc_auc_score, matthews_corrcoef
	Generator = np.random.default_rng(1)
	for Trial in range(200):
		Count = int(Generator.integers(20, 400))
		TrueScores = np.round(Generator.normal(size=Count), 1)
		ModelScores = np.round(TrueScores + Generator.normal(size=Count), 1)
		Labels = (TrueScores > np.median(TrueScores)).astype(int)
		assert abs(SpearmanFromRanks(TrueScores, ModelScores) - spearmanr(TrueScores, ModelScores)[0]) < 1e-12
		assert abs(AreaUnderRoc(Labels, ModelScores) - roc_auc_score(Labels, ModelScores)) < 1e-12
		Predictions = (ModelScores >= np.median(ModelScores)).astype(int)
		assert abs(MatthewsCorrelation(Labels, Predictions) - matthews_corrcoef(Labels, Predictions)) < 1e-12
	# A perfect ranking gives NDCG 1 and recall 1, a reversed one gives recall 0
	Values = np.arange(100, dtype=float)
	assert abs(NdcgTopTenPercent(Values, Values) - 1.0) < 1e-12
	assert TopTenPercentRecall(Values, Values) == 1.0 and TopTenPercentRecall(Values, -Values) == 0.0
	print("selftest ok")

MetricFunctions = {
	"Spearman": lambda Frame, Column: SpearmanFromRanks(Frame["DMS_score"].values, Frame[Column].values),
	"AUC": lambda Frame, Column: AreaUnderRoc(Frame["DMS_score_bin"].values, Frame[Column].values),
	"MCC": lambda Frame, Column: MccAtModelMedian(Frame["DMS_score_bin"].values, Frame[Column].values),
	"NDCG": lambda Frame, Column: NdcgTopTenPercent(Frame["DMS_score"].values, Frame[Column].values),
	"Top_recall": lambda Frame, Column: TopTenPercentRecall(Frame["DMS_score"].values, Frame[Column].values),
}

# Score folder, column written by compute_fitness, column in the authors' tables, metrics to compute
Models = [
	("ESM1b", "esm1b_t33_650M_UR50S", "ESM-1b", ["Spearman", "AUC", "MCC", "NDCG", "Top_recall"]),
	("ESM2/8M", "esm2_t6_8M_UR50D", "ESM2 (8M)", ["Spearman"]),
	("ESM2/35M", "esm2_t12_35M_UR50D", "ESM2 (35M)", ["Spearman"]),
	("ESM2/150M", "esm2_t30_150M_UR50D", "ESM2 (150M)", ["Spearman"]),
	("ESM2/650M", "esm2_t33_650M_UR50D", "ESM2 (650M)", ["Spearman"]),
]

def Main(Repo, VerifyFolder):
	Reference = pd.read_csv(f"{Repo}/reference_files/DMS_substitutions.csv")
	TablesFolder = f"{Repo}/benchmarks/DMS_zero_shot/substitutions"
	Rows = []
	for Folder, Column, AuthorsColumn, MetricNames in Models:
		AuthorsTables = {MetricName: pd.read_csv(f"{TablesFolder}/{MetricName}/DMS_substitutions_{MetricName}_DMS_level.csv").set_index("DMS ID") for MetricName in MetricNames}
		for _, Assay in Reference.iterrows():
			ScorePath = f"{VerifyFolder}/scores/{Folder}/{Assay['DMS_id']}.csv"
			if not os.path.exists(ScorePath):
				continue
			Frame = pd.read_csv(ScorePath)
			# Every mutant of the assay must be scored, nothing dropped
			assert len(Frame) == Assay["DMS_total_number_mutants"], Assay["DMS_id"]
			assert Frame[Column].notna().all(), Assay["DMS_id"]
			for MetricName in MetricNames:
				Rows.append({"model": AuthorsColumn, "metric": MetricName, "DMS_id": Assay["DMS_id"], "UniProt_ID": Assay["UniProt_ID"], "Selection Type": Assay["coarse_selection_type"], "n_mutants": len(Frame), "seq_len": Assay["seq_len"], "value": MetricFunctions[MetricName](Frame, Column), "authors": float(AuthorsTables[MetricName].loc[Assay["DMS_id"], AuthorsColumn])})
	PerAssay = pd.DataFrame(Rows)
	PerAssay["diff"] = PerAssay["value"] - PerAssay["authors"]
	PerAssay.to_csv(f"{VerifyFolder}/per_assay_metrics.csv", index=False)

	Summary = {}
	for (Model, MetricName), Group in PerAssay.groupby(["model", "metric"], sort=False):
		Authors = Group.assign(value=Group["authors"])
		Summary[f"{Model}|{MetricName}"] = {
			"assays": int(len(Group)),
			"mutants": int(Group["n_mutants"].sum()),
			"ours_code": CorrectedAverageCode(Group),
			"ours_literal": CorrectedAverageLiteral(Group),
			"authors_same_assays_code": CorrectedAverageCode(Authors),
			"authors_same_assays_literal": CorrectedAverageLiteral(Authors),
			"max_abs_diff_vs_authors_3dp": float(Group["diff"].abs().max()),
			"assays_abs_diff_over_0.0015": int((Group["diff"].abs() > 0.0015).sum()),
			"assays_abs_diff_over_0.01": int((Group["diff"].abs() > 0.01).sum()),
			"mean_diff": float(Group["diff"].mean()),
			"worst_assays": Group.reindex(Group["diff"].abs().sort_values(ascending=False).index)[["DMS_id", "seq_len", "value", "authors", "diff"]].head(5).round(4).values.tolist(),
		}
	with open(f"{VerifyFolder}/summary.json", "w") as File:
		json.dump(Summary, File, indent=1)
	for Key, Values in Summary.items():
		print(Key, {Name: (round(Value, 4) if isinstance(Value, float) else Value) for Name, Value in Values.items() if Name != "worst_assays"})
		print("   worst:", Values["worst_assays"])

if __name__ == "__main__":
	if sys.argv[1] == "--selftest":
		SelfTest()
	else:
		Main(sys.argv[1], sys.argv[2])
