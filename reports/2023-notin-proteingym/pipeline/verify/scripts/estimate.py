# GPU-hour estimate for masked-marginals: (seq_len + 2) forwards per assay at min(seq_len + 2, 1024) tokens
import sys
import numpy as np
import pandas as pd

Reference = pd.read_csv(sys.argv[1])
Lengths = [100, 300, 600, 1024]
MillisecondsBySize = {"8M": [10, 10, 10, 18], "35M": [19, 19, 22, 49], "150M": [31, 40, 64, 113], "650M": [50, 99, 184, 299]}
Tokens = np.minimum(Reference["seq_len"].values + 2, 1024)
Passes = Reference["seq_len"].values + 2
UniqueSequences = Reference.drop_duplicates("target_seq")
UniqueTokens = np.minimum(UniqueSequences["seq_len"].values + 2, 1024)
UniquePasses = UniqueSequences["seq_len"].values + 2
print("assays", len(Reference), "unique target_seq", len(UniqueSequences), "sum seq_len", Reference["seq_len"].sum(), "mutants", Reference["DMS_total_number_mutants"].sum())
for Size, Milliseconds in MillisecondsBySize.items():
	Hours = (Passes * np.interp(Tokens, Lengths, Milliseconds)).sum() / 1000 / 3600
	UniqueHours = (UniquePasses * np.interp(UniqueTokens, Lengths, Milliseconds)).sum() / 1000 / 3600
	print(f"{Size}: all assays {Hours:.2f} h, unique sequences {UniqueHours:.2f} h")

# Cumulative 650M hours along the pre-drawn assay order
Order = pd.read_csv(sys.argv[2])
OrderedLengths = Order["seq_len"].values
OrderedHours = np.cumsum((OrderedLengths + 2) * np.interp(np.minimum(OrderedLengths + 2, 1024), Lengths, MillisecondsBySize["650M"])) / 1000 / 3600
for Count in [30, 40, 50, 54, 60, 70, 80, 100]:
	print(f"650M first {Count} of the order: {OrderedHours[Count - 1]:.2f} h")
