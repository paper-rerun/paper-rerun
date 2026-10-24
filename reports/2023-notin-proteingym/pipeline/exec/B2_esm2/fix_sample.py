# Fix the sample size before any run: the full 217 for 8M, the first 30 of sample_order.json for 35M, 150M and 650M
# Reason: estimate.py puts the full recompute at 3.5 h (8M) + 4.1 h (35M) + 8.9 h (150M) + 10.0 h (650M), far over the ~4 h budget,
# and the ESM-1b block (B1) shares the same GPU. 30 assays of each larger size cost about 3.3 h on top of the 8M run
import json
Order = json.load(open("sample_order.json"))
Sample = {"fixed_at": "2026-10-23 17:25 -03, before any ESM2 score was computed or read (only the 8M smoke test of index 17 from the env stage existed)",
	"N_larger_sizes": 30, "8M": list(range(217)), "35M": Order["order"][:30], "150M": Order["order"][:30], "650M": Order["order"][:30],
	"sample_DMS_ids": Order["DMS_id_order"][:30]}
json.dump(Sample, open("sample.json", "w"), indent=1)
