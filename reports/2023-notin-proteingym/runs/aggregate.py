"""Corrected average of per-DMS Spearman, two ways.
literal: mean over assays within each coarse_selection_type, then mean of the 5 (paper A.5.1 text)
repo:    mean per (UniProt_ID, type), then per type, then mean of the 5 (performance_DMS_benchmarks.py)
Usage: aggregate.py <DMS_level.csv> <reference DMS_substitutions.csv> col1 [col2 ...]"""
import sys
import pandas as pd

def corrected_averages(per_dms, reference, column):
	# Join per-DMS values with the assay metadata from the reference file
	ref = reference[["DMS_id", "UniProt_ID", "coarse_selection_type"]]
	df = ref.merge(per_dms[[column]], left_on="DMS_id", right_index=True, how="left")
	assert df[column].notna().all(), f"missing assays for {column}"
	literal = df.groupby("coarse_selection_type")[column].mean().mean()
	repo = df.groupby(["UniProt_ID", "coarse_selection_type"])[column].mean().groupby("coarse_selection_type").mean().mean()
	return literal, repo, len(df)

if __name__ == "__main__":
	per_dms = pd.read_csv(sys.argv[1]).set_index(pd.read_csv(sys.argv[1]).columns[0])
	reference = pd.read_csv(sys.argv[2])
	for column in sys.argv[3:]:
		literal, repo, n = corrected_averages(per_dms, reference, column)
		print(f"{column:14s} n={n} literal={literal:.4f} repo={repo:.4f}")
