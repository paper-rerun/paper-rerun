# Early per-mutant check of the finished assays against the authors' ESM1b column
import glob, os
import pandas as pd
B = "/mnt/e/Ciencia/pipeline/2023-notin-proteingym/exec/B1_esm1b"
for Path in sorted(glob.glob(B + "/scores/ESM1b/*.csv")):
	DmsId = os.path.basename(Path)[:-4]
	Ours = pd.read_csv(Path, usecols=["mutant", "esm1b_t33_650M_UR50S"])
	Theirs = pd.read_csv(f"{B}/authors_merged/{DmsId}.csv", usecols=["mutant", "ESM1b"])
	Merged = Ours.merge(Theirs, on="mutant")
	Diff = (Merged.esm1b_t33_650M_UR50S - Merged.ESM1b).abs()
	print(f"{DmsId:45s} n={len(Ours):6d}/{len(Theirs):6d} merged={len(Merged):6d} maxdiff={Diff.max():.2e} spearman={Merged.esm1b_t33_650M_UR50S.corr(Merged.ESM1b, method='spearman'):.5f}")
