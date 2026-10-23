"""auPRC on a subsampled test set, weighted back to the full set

Reads the chunk files of one task that already have predictions (chunk order = positives, then negatives by u),
so the negatives present are exactly those with u <= u of the last one: a Bernoulli sample at that rate.
Positives weigh 1/positive_rate, negatives 1/negative_rate. CI: percentile bootstrap, classes resampled apart.
Usage: score_sample.py <chunk dir> <run dir> <positive rate> [--uniform]   (--uniform: plain AP, for the valid check)
"""
import glob
import os
import sys
import numpy as np
import pandas as pd
from sklearn.metrics import average_precision_score


def WeightedAuprc(Labels, Scores, NegativeRate, PositiveRate=1.0):
	Weights = np.where(Labels == 1, 1.0 / PositiveRate, 1.0 / NegativeRate)
	return average_precision_score(Labels, Scores, sample_weight=Weights)


def main():
	ChunkDirectory, RunDirectory, PositiveRate = sys.argv[1], sys.argv[2], float(sys.argv[3])
	bUniform = "--uniform" in sys.argv
	LabelParts, ScoreParts, UniformParts = [], [], []
	for ChunkPath in sorted(glob.glob(os.path.join(ChunkDirectory, "chunk_*.tsv"))):
		PredictionsPath = os.path.join(RunDirectory, os.path.basename(ChunkPath).split(".")[0] + "_predictions.tsv")
		# Stop at the first chunk without predictions so the prefix stays contiguous
		if not os.path.exists(PredictionsPath):
			break
		Chunk = pd.read_csv(ChunkPath, sep="\t", usecols=["label", "u"])
		Predictions = pd.read_csv(PredictionsPath, sep="\t")
		assert len(Chunk) == len(Predictions) and (Chunk["label"].values == Predictions["label"].values).all()
		LabelParts.append(Chunk["label"].values)
		UniformParts.append(Chunk["u"].values)
		ScoreParts.append(Predictions["prediction"].values)
	Labels, Scores, Uniforms = np.concatenate(LabelParts), np.concatenate(ScoreParts), np.concatenate(UniformParts)
	NegativeRate = 1.0 if bUniform else float(Uniforms[Labels == 0].max())
	PointEstimate = WeightedAuprc(Labels, Scores, NegativeRate, PositiveRate)

	RandomGenerator = np.random.default_rng(0)
	PositiveIndices, NegativeIndices = np.flatnonzero(Labels == 1), np.flatnonzero(Labels == 0)
	BootstrapValues = []
	for _ in range(200):
		Indices = np.concatenate([RandomGenerator.choice(PositiveIndices, len(PositiveIndices)), RandomGenerator.choice(NegativeIndices, len(NegativeIndices))])
		BootstrapValues.append(WeightedAuprc(Labels[Indices], Scores[Indices], NegativeRate, PositiveRate))
	Low, High = np.percentile(BootstrapValues, [2.5, 97.5])
	print(f"{os.path.basename(ChunkDirectory)}\tchunks={len(LabelParts)}\tpos={len(PositiveIndices)}\tneg={len(NegativeIndices)}\tpos_rate={PositiveRate}\tneg_rate={NegativeRate:.5f}\tauPRC={PointEstimate:.4f}\tCI95=[{Low:.4f},{High:.4f}]")


if __name__ == "__main__":
	main()
