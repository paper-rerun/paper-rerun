"""Decides what "validity" and "uniqueness" mean, before anything of ours is sampled.

No code in DrugEx computes a uniqueness ratio, so the definition behind Table S4 is not in
the release. What is in the deposit is every molecule the authors sampled, with their own
Valid and Unique flag on each row. This recomputes both ratios from those molecules under
every reading that makes sense, with RDKit doing the parsing, and prints them next to the
published values. Whichever reading reproduces the published number is the definition we
freeze and then measure our own sampling against.

Readings tried, for n sampled rows:
  validity   = parseable / n, and parseable-and-single-fragment / n
  uniqueness = distinct raw strings / n, distinct canonical / n,
               distinct canonical among valid / valid, distinct canonical among valid / n

Run it with -P and the paths as arguments. Streams the .xz, nothing unpacked to disk.
"""
import collections
import json
import lzma
import sys

from rdkit import Chem, RDLogger

RDLogger.DisableLog("rdApp.*")

PATH, OUT = sys.argv[1], sys.argv[2]
WANTED = {("ChEMBL 27", "sequence LSTM RNN"), ("ChEMBL 31", "sequence GRU RNN")}

acc = collections.defaultdict(lambda: {
	"n": 0, "their_valid": 0, "their_unique": 0,
	"parseable": 0, "single_fragment": 0,
	"raw": set(), "canon": set(), "canon_valid": set()})

with lzma.open(PATH, "rt", encoding="utf-8") as fh:
	header = fh.readline().rstrip("\n").split("\t")
	col = {name: i for i, name in enumerate(header)}
	for line in fh:
		f = line.rstrip("\n").split("\t")
		if len(f) != len(header):
			continue
		key = (f[col["dataset"]], f[col["DrugEx version"]])
		if key not in WANTED:
			continue
		a = acc[(f[col["Machine"]],) + key]
		smi = f[col["SMILES"]]
		a["n"] += 1
		a["their_valid"] += f[col["Valid"]] == "1.0"
		a["their_unique"] += f[col["Unique"]] == "1"
		a["raw"].add(smi)

		mol = Chem.MolFromSmiles(smi)
		if mol is None:
			continue
		a["parseable"] += 1
		canon = Chem.MolToSmiles(mol)
		a["canon"].add(canon)
		a["canon_valid"].add(canon)
		# DrugEx treats a multi-fragment SMILES as invalid by default (no_multifrag_smiles=True)
		if "." not in canon:
			a["single_fragment"] += 1

out = {}
for cell, a in sorted(acc.items()):
	n = a["n"]
	valid = a["parseable"]
	out["|".join(cell)] = {
		"n": n,
		"validity_their_flag": a["their_valid"] / n,
		"validity_parseable": valid / n,
		"validity_single_fragment": a["single_fragment"] / n,
		"uniqueness_their_flag": a["their_unique"] / n,
		"uniqueness_distinct_raw_over_n": len(a["raw"]) / n,
		"uniqueness_distinct_canonical_over_n": len(a["canon"]) / n,
		"uniqueness_distinct_canonical_over_valid": len(a["canon_valid"]) / valid if valid else None,
		"distinct_canonical": len(a["canon"]),
	}
open(OUT, "w", encoding="utf-8", newline="\n").write(json.dumps(out, indent=1))
print(json.dumps(out, indent=1))
