"""How close complete genes sit to the busco-mode length threshold (length - 2 sigma), per genome"""
import csv
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
for tag, lineage in [("scer", "saccharomycetes"), ("zmay", "liliopsida"), ("hsap", "primates")]:
	cutoff = {}
	for line in open(ROOT / "data/mb_downloads" / f"{lineage}_odb10" / "lengths_cutoff"):
		parts = line.split()
		sigma = float(parts[2]) or 1.0
		cutoff[parts[0]] = float(parts[3]) - 2 * sigma
	best_length = {}
	with open(ROOT / "runs" / tag / f"{lineage}_odb10" / "full_table.tsv") as handle:
		for row in csv.DictReader(handle, delimiter="\t"):
			if row["Status"] in ("Single", "Duplicated"):
				best_length[row["Gene"]] = max(best_length.get(row["Gene"], 0), float(row["Length"]))
	margins = [best_length[g] / cutoff[g] for g in best_length]
	near_5 = sum(1 for m in margins if m < 1.05)
	near_10 = sum(1 for m in margins if m < 1.10)
	print(f"{tag}: complete={len(margins)} within5%={near_5} within10%={near_10} below1={sum(1 for m in margins if m < 1.0)}")
