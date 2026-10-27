# Compare the sequence of each v6 PDB we downloaded with the ungapped sequence of the same member in the
# authors' published FoldMason MSA (built from v4). Also flags members the server no longer has.
# Usage: python3 -I compare_sequences.py <project root>
import csv
import os
import sys

ROOT = sys.argv[1]
THREE = {"ALA": "A", "ARG": "R", "ASN": "N", "ASP": "D", "CYS": "C", "GLN": "Q", "GLU": "E", "GLY": "G", "HIS": "H",
	"ILE": "I", "LEU": "L", "LYS": "K", "MET": "M", "PHE": "F", "PRO": "P", "SER": "S", "THR": "T", "TRP": "W",
	"TYR": "Y", "VAL": "V", "UNK": "X"}

def pdb_sequence(path):
	residues = []
	for line in open(path):
		if line.startswith("ATOM") and line[12:16].strip() == "CA":
			residues.append(THREE.get(line[17:20], "X"))
	return "".join(residues)

def read_fasta(path):
	records = {}
	name = None
	for line in open(path):
		line = line.strip()
		if line.startswith(">"):
			name = line[1:].split()[0]
			records[name] = []
		elif name:
			records[name].append(line)
	return {k: "".join(v).replace("-", "").upper() for k, v in records.items()}

analysis = ROOT + "/sources/analysis"
R = open(analysis + "/FoldMason_benchmarks.R").read()
start = R.index("afdb.training <- c(")
body = R[start:R.index(")", start)]
TRAIN = {x.strip().strip('"') for x in body.split("c(", 1)[1].split(",") if x.strip()}

totals = {"members": 0, "v6_missing": 0, "same_seq": 0, "diff_seq": 0}
per_cluster = []
with open(ROOT + "/runs/v4_vs_v6/sequence_check.tsv", "w") as out:
	out.write("cluster\tmember\tstatus\tv4_len\tv6_len\n")
	for acc, cath, nummem, numdom, members in csv.reader(open(analysis + "/data/afdb_families.tsv"), delimiter="\t"):
		if acc in TRAIN:
			continue
		authors = read_fasta(f"{ROOT}/data/zenodo_extract/afdb_clusters/{acc}/foldmason_aa.fa")
		changed = 0
		missing = 0
		for member in members.split(","):
			name = f"AF-{member}-F1-model_v4"
			totals["members"] += 1
			v4 = authors.get(name, "")
			path = f"{ROOT}/data/afdb_clusters/{acc}/pdbs/{name}.pdb"
			if not os.path.exists(path):
				status = "v6_missing"
				missing += 1
				v6 = ""
			else:
				v6 = pdb_sequence(path)
				status = "same_seq" if v6 == v4 else "diff_seq"
				changed += status == "diff_seq"
			totals[status] += 1
			out.write(f"{acc}\t{member}\t{status}\t{len(v4)}\t{len(v6)}\n")
		per_cluster.append((acc, numdom, missing, changed))

with open(ROOT + "/runs/v4_vs_v6/sequence_check_per_cluster.tsv", "w") as out:
	out.write("cluster\tdomains\tmissing\tseq_changed\n")
	for row in per_cluster:
		out.write("\t".join(map(str, row)) + "\n")
print(totals)
print("clusters with all 20 members present and unchanged sequence:", sum(1 for r in per_cluster if r[2] == 0 and r[3] == 0))
print("clusters with at least one missing member:", sum(1 for r in per_cluster if r[2] > 0))
