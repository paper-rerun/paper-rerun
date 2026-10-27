# Build the aria2c input list for the 160 benchmark clusters (200 minus the authors' 40 training clusters)
# v4 files are gone from the AFDB server, so we fetch model_v6 and save it under the authors' v4 file name
# Usage: python3 -I make_aria_list.py <sources/analysis> <data/afdb_clusters> <out_list>
import csv
import sys

ANALYSIS, DATA, OUT = sys.argv[1], sys.argv[2], sys.argv[3]
R = open(ANALYSIS + "/FoldMason_benchmarks.R").read()
start = R.index("afdb.training <- c(")
body = R[start:R.index(")", start)]
TRAIN = {x.strip().strip('"') for x in body.split("c(", 1)[1].split(",") if x.strip()}
assert len(TRAIN) == 40

n_clusters = 0
n_files = 0
with open(OUT, "w") as out:
	for acc, cath, nummem, numdom, members in csv.reader(open(ANALYSIS + "/data/afdb_families.tsv"), delimiter="\t"):
		if acc in TRAIN:
			continue
		n_clusters += 1
		for member in members.split(","):
			out.write(f"https://alphafold.ebi.ac.uk/files/AF-{member}-F1-model_v6.pdb\n")
			out.write(f"  dir={DATA}/{acc}/pdbs\n")
			out.write(f"  out=AF-{member}-F1-model_v4.pdb\n")
			n_files += 1
print("clusters", n_clusters, "files", n_files)
assert n_clusters == 160
