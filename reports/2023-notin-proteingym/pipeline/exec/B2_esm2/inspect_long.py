# Where along the sequence do our and the authors' scores differ, for one long assay? Per mutated position: mean |diff|
import sys
import pandas as pd
Size, DmsId, Column = sys.argv[1], sys.argv[2], sys.argv[3]
Ours = pd.read_csv(f"scores/ESM2/{Size}/{DmsId}.csv", usecols=["mutant", Column])
Theirs = pd.read_csv(f"authors_merged/{DmsId}.csv", usecols=["mutant", f"ESM2_{Size}"])
Merged = Ours.merge(Theirs, on="mutant")
Merged = Merged[~Merged.mutant.str.contains(":")]
Merged["pos"] = Merged.mutant.str[1:-1].astype(int)
Merged["absdiff"] = (Merged[Column] - Merged[f"ESM2_{Size}"]).abs()
ByPos = Merged.groupby("pos").absdiff.max()
print("singles", len(Merged), "positions", len(ByPos), "pos range", ByPos.index.min(), ByPos.index.max())
Bad = ByPos[ByPos > 1e-3]
print("positions with max|diff|>1e-3:", len(Bad), "range", Bad.index.min() if len(Bad) else None, Bad.index.max() if len(Bad) else None)
Good = ByPos[ByPos <= 1e-3]
print("good range", Good.index.min() if len(Good) else None, Good.index.max() if len(Good) else None)
print(ByPos.iloc[::max(1, len(ByPos)//40)].round(4).to_string())
