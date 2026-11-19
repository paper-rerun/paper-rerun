"""Recounts Table S4 from the authors' own sampled molecules.

The deposit (10.5281/zenodo.7928362) ships every molecule they sampled, with their own
Valid / Unique / Novel flag on each row. So the table can be recounted without sampling
anything: it separates "their model samples this" from "their script counts it this way",
and it fixes the one definition the repository does not contain, since no code in DrugEx
computes a uniqueness ratio.

Streams the .xz line by line. The file is 496 MB unpacked and never lands on disk.
Run it with -P and the path as an argument.
"""
import collections
import json
import lzma
import sys

PATH, OUT = sys.argv[1], sys.argv[2]

# Only the two RNNs of the target; the transformers are out (their test split was never published)
WANTED = {("ChEMBL 27", "sequence LSTM RNN"), ("ChEMBL 31", "sequence GRU RNN")}


def flag(text):
	"""The flag columns carry 1, 0 or a dash where the metric does not apply."""
	if text in ("-", ""):
		return False
	return float(text) == 1.0


rows = collections.defaultdict(lambda: {"n": 0, "valid_flag": 0, "unique_flag": 0,
	"novel_flag": 0, "valid_and_unique": 0})
smiles_seen = collections.defaultdict(set)
smiles_valid_seen = collections.defaultdict(set)

with lzma.open(PATH, "rt", encoding="utf-8") as fh:
	header = fh.readline().rstrip("\n").split("\t")
	col = {name: i for i, name in enumerate(header)}
	for line in fh:
		f = line.rstrip("\n").split("\t")
		# The deposit writes a blank line between every row, so half the lines are empty
		if len(f) != len(header):
			continue
		key = (f[col["dataset"]], f[col["DrugEx version"]])
		if key not in WANTED:
			continue
		cell = (f[col["Machine"]],) + key
		r = rows[cell]
		r["n"] += 1
		valid = flag(f[col["Valid"]])
		unique = flag(f[col["Unique"]])
		r["valid_flag"] += valid
		r["unique_flag"] += unique
		# Novel is "-" on the RNN rows, so it counts as not set rather than as zero
		r["novel_flag"] += flag(f[col["Novel"]])
		r["valid_and_unique"] += valid and unique
		smi = f[col["SMILES"]]
		smiles_seen[cell].add(smi)
		if valid:
			smiles_valid_seen[cell].add(smi)

out = {}
for cell, r in sorted(rows.items()):
	n = r["n"]
	out["|".join(cell)] = {
		"n": n,
		# The three candidate readings of "ratio of unique molecules"
		"unique_flag_over_n": r["unique_flag"] / n,
		"unique_flag_over_valid": r["unique_flag"] / r["valid_flag"] if r["valid_flag"] else None,
		"distinct_smiles_over_n": len(smiles_seen[cell]) / n,
		"distinct_valid_smiles_over_valid": (len(smiles_valid_seen[cell]) / r["valid_flag"]
			if r["valid_flag"] else None),
		"valid_flag_over_n": r["valid_flag"] / n,
		"novel_flag_over_n": r["novel_flag"] / n,
		"valid_and_unique_over_n": r["valid_and_unique"] / n,
		"distinct_smiles": len(smiles_seen[cell]),
		"distinct_valid_smiles": len(smiles_valid_seen[cell]),
	}
open(OUT, "w", encoding="utf-8", newline="\n").write(json.dumps(out, indent=1))
print(json.dumps(out, indent=1))
