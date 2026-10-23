"""Turn each stream sample into ordered chunk files for predict_XGBoost.py

Order: chosen positives first, then negatives by ascending u. Any prefix that ends inside the negatives is a
Bernoulli sample of negatives at rate = u of its last row, so the run can stop or grow without re-sampling.
"""
import os
import numpy as np
import pandas as pd

Root = "/mnt/e/Ciencia/artigos/2025-zhai-plantcad"
ChunkRows = 8000
# task name -> (sample file, positive keep rate, max negative rate)
Tasks = {
	"TIS_sorghum": ("data/TIS/test_sorghum.sample.tsv", 1.0, 0.02),
	"TIS_maize": ("data/TIS/test_maize.sample.tsv", 1.0, 0.006),
	"Donor_sorghum": ("data/Donor/test_sorghum.sample.tsv", 0.25, 0.006),
	"Donor_maize": ("data/Donor/test_maize.sample.tsv", 0.25, 0.002),
}

for TaskName, (SamplePath, PositiveRate, MaxNegativeRate) in Tasks.items():
	Sample = pd.read_csv(os.path.join(Root, SamplePath), sep="\t")
	Positives = Sample[(Sample["label"] == 1) & (Sample["u"] < PositiveRate)]
	Negatives = Sample[(Sample["label"] == 0) & (Sample["u"] < MaxNegativeRate)].sort_values("u", kind="stable")
	Ordered = pd.concat([Positives, Negatives])
	ChunkDirectory = os.path.join(Root, "chunks", TaskName)
	os.makedirs(ChunkDirectory, exist_ok=True)
	for ChunkIndex, Start in enumerate(range(0, len(Ordered), ChunkRows)):
		Ordered.iloc[Start:Start + ChunkRows].to_csv(os.path.join(ChunkDirectory, f"chunk_{ChunkIndex:03d}.tsv"), sep="\t", index=False)
	print(f"{TaskName}: pos={len(Positives)} (rate {PositiveRate}) neg={len(Negatives)} (max rate {MaxNegativeRate}) chunks={ChunkIndex + 1}")

# Arabidopsis validation sanity check: 8000 rows drawn uniformly, same class ratio as the full set
for Task in ("TIS", "Donor"):
	Valid = pd.read_csv(os.path.join(Root, f"data/{Task}/valid.tsv"), sep="\t").sample(n=ChunkRows, random_state=0)
	Valid["u"] = 0.0
	ChunkDirectory = os.path.join(Root, "chunks", f"{Task}_valid")
	os.makedirs(ChunkDirectory, exist_ok=True)
	Valid.to_csv(os.path.join(ChunkDirectory, "chunk_000.tsv"), sep="\t", index=False)
	print(f"{Task}_valid: pos={int(Valid['label'].sum())} neg={int((Valid['label'] == 0).sum())}")
