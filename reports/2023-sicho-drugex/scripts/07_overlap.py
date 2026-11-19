"""Checks our sample against the authors' sample, molecule by molecule.

The ratios agreeing is one thing; sampling the same distribution is another. This takes the
canonical molecules we sampled and the ones the authors deposited for the same model, and
reports how much of each set the other covers. A model sampled from different weights, or
decoded through a different vocabulary, would not share most of its molecules.

The comparison is per machine, because each of the authors' machines is its own independent
draw of 100000, and two of their own machines overlap by only as much as chance and the
model's concentration allow — which is the number our overlap has to be read against.

Usage: 07_overlap.py <tsv.xz> <our_c27_smiles.txt.gz> <our_c31_smiles.txt.gz> <out.json>
"""
import collections
import gzip
import itertools
import json
import lzma
import sys

from rdkit import Chem, RDLogger

RDLogger.DisableLog("rdApp.*")

TSV, OURS_27, OURS_31, OUT = sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4]
MODELS = {"ChEMBL 27": "sequence LSTM RNN", "ChEMBL 31": "sequence GRU RNN"}


def canonical_set(smiles_iter):
	out = set()
	for smi in smiles_iter:
		smi = smi.strip()
		if not smi:
			continue
		mol = Chem.MolFromSmiles(smi)
		if mol is None:
			continue
		canon = Chem.MolToSmiles(mol)
		if "." not in canon:
			out.add(canon)
	return out


ours = {}
with gzip.open(OURS_27, "rt", encoding="utf-8") as fh:
	ours["ChEMBL 27"] = canonical_set(fh)
with gzip.open(OURS_31, "rt", encoding="utf-8") as fh:
	ours["ChEMBL 31"] = canonical_set(fh)

theirs = collections.defaultdict(set)
rejected = collections.defaultdict(int)
with lzma.open(TSV, "rt", encoding="utf-8") as fh:
	header = fh.readline().rstrip("\n").split("\t")
	col = {name: i for i, name in enumerate(header)}
	for line in fh:
		f = line.rstrip("\n").split("\t")
		if len(f) != len(header):
			continue
		dataset, version = f[col["dataset"]], f[col["DrugEx version"]]
		if MODELS.get(dataset) != version:
			continue
		if f[col["Valid"]] != "1.0":
			continue
		mol = Chem.MolFromSmiles(f[col["SMILES"]])
		if mol is None:
			# They flagged it valid and this RDKit does not parse it: count, do not crash
			rejected[(dataset, f[col["Machine"]])] += 1
			continue
		canon = Chem.MolToSmiles(mol)
		if "." not in canon:
			theirs[(dataset, f[col["Machine"]])].add(canon)

out = {}
for dataset in MODELS:
	machines = sorted(m for (d, m) in theirs if d == dataset)
	ours_set = ours[dataset]
	entry = {"ours_distinct": len(ours_set), "per_machine": {}, "their_machine_pairs": {},
		"their_rows_flagged_valid_that_this_rdkit_rejects": {m: rejected[(dataset, m)] for m in machines}}
	for machine in machines:
		t = theirs[(dataset, machine)]
		shared = len(ours_set & t)
		entry["per_machine"][machine] = {
			"theirs_distinct": len(t),
			"shared": shared,
			"share_of_ours": shared / len(ours_set) if ours_set else None,
			"share_of_theirs": shared / len(t) if t else None,
		}
	# Their own machines against each other, as the yardstick for the numbers above
	for a, b in itertools.combinations(machines, 2):
		sa, sb = theirs[(dataset, a)], theirs[(dataset, b)]
		shared = len(sa & sb)
		entry["their_machine_pairs"]["%s-%s" % (a, b)] = {
			"shared": shared,
			"share_of_first": shared / len(sa) if sa else None,
		}
	out[dataset] = entry

open(OUT, "w", encoding="utf-8", newline="\n").write(json.dumps(out, indent=1))
print(json.dumps(out, indent=1))
