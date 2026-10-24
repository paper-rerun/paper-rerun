"""Per-assay Spearman and corrected averages for one model's per-mutant score files.

Spearman per assay: scipy spearmanr(DMS_score, score), rounded to 3 decimals as in
performance_DMS_benchmarks.py (PG_v1.3). Two aggregations:
  repo:    mean per (UniProt_ID, coarse_selection_type), then per type, then mean of the 5 types
  literal: mean over assays per coarse_selection_type, then mean of the 5 types (paper A.5.1 text)
Also reports the unrounded repo value.

Usage: evaluate.py <score_dir> <score_column> <label> [out_csv]
score_dir holds one <DMS_id>.csv per assay with DMS_score and <score_column>.
"""
import os
import sys
import pandas as pd
from scipy.stats import spearmanr

REFERENCE = "/mnt/e/Ciencia/meio/2023-notin-proteingym/repo/reference_files/DMS_substitutions.csv"


def CorrectedAverages(PerAssay, Column):
	# Protein first, then function type, then the 5 types (what the authors' script does)
	Repo = PerAssay.groupby(["UniProt_ID", "coarse_selection_type"])[Column].mean().groupby("coarse_selection_type").mean().mean()
	# Assays straight into function types (what the paper text says)
	Literal = PerAssay.groupby("coarse_selection_type")[Column].mean().mean()
	return Repo, Literal


def Main():
	ScoreDir, ScoreColumn, Label = sys.argv[1:4]
	Reference = pd.read_csv(REFERENCE)
	Rows = []
	for _, Assay in Reference.iterrows():
		ScoreFile = ScoreDir + os.sep + Assay["DMS_id"] + ".csv"
		if not os.path.exists(ScoreFile):
			continue
		Scores = pd.read_csv(ScoreFile)
		# Every mutant must have a score, the authors assume no missing values
		assert Scores[ScoreColumn].notna().all(), ScoreFile
		Rho = spearmanr(Scores["DMS_score"], Scores[ScoreColumn])[0]
		Rows.append({"DMS_id": Assay["DMS_id"], "UniProt_ID": Assay["UniProt_ID"], "coarse_selection_type": Assay["coarse_selection_type"], "n_mutants": len(Scores), "spearman_raw": Rho, "spearman": round(Rho, 3)})
	PerAssay = pd.DataFrame(Rows)
	Repo, Literal = CorrectedAverages(PerAssay, "spearman")
	RepoRaw, _ = CorrectedAverages(PerAssay, "spearman_raw")
	print(f"{Label:12s} assays={len(PerAssay)} mutants={PerAssay.n_mutants.sum()} repo={Repo:.4f} repo_unrounded={RepoRaw:.4f} literal={Literal:.4f} plain_mean={PerAssay.spearman.mean():.4f}")
	if len(sys.argv) > 4:
		PerAssay.to_csv(sys.argv[4], index=False)


if __name__ == "__main__":
	Main()
