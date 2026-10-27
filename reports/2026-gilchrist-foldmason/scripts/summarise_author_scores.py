# Aggregate the authors' published per-family scores (no run of ours) following FoldMason_benchmarks.R
# Usage: python3 -I summarise_author_scores.py <sources/analysis>
import csv, sys, math, statistics as st
from collections import defaultdict

D = sys.argv[1]
R = open(D + "/FoldMason_benchmarks.R").read()

def r_vector(name):
	# Read a c("..") vector straight from the authors' R script so the lists are theirs
	start = R.index(name + " <- c(")
	body = R[start:R.index(")", start)]
	return [x.strip().strip('"') for x in body.split("c(", 1)[1].split(",") if x.strip()]

HARD = set(r_vector("homstrad.hard"))
TRAIN = set(r_vector("afdb.training"))
print("hard", len(HARD), "train", len(TRAIN))

counts = {r[0]: int(r[1]) for r in csv.reader(open(D + "/data/homstrad_families.tsv"), delimiter="\t")}
rows = list(csv.reader(open(D + "/data/homstrad_scores.tsv"), delimiter="\t"))
print("homstrad tools with sp rows:", sorted({r[1] for r in rows if r[2].startswith("sp_")}))
values = defaultdict(list)
for family, tool, kind, score in rows:
	if not kind.startswith("sp_") or counts.get(family, 0) < 2 or tool == "foldmason_refine100":
		continue
	if tool == "foldmason_refine100_rosc":
		tool = "foldmason_refine100"
	values[(tool, kind, "full")].append(float(score))
	if family in HARD:
		values[(tool, kind, "hard")].append(float(score))

def describe(v):
	sd = st.stdev(v)
	return f"n={len(v)} mean={st.mean(v):.6f} sd={sd:.4f} sem={sd / math.sqrt(len(v)):.4f}"

for subset in ("full", "hard"):
	for tool in ("foldmason", "foldmason_fast", "foldmason_refine100"):
		forward = values[(tool, "sp_fwd", subset)]
		reverse = values[(tool, "sp_rev", subset)]
		mf, mr = st.mean(forward), st.mean(reverse)
		print(f"HOMSTRAD {subset} {tool} fwd {describe(forward)} | rev {describe(reverse)} | f1={2 * mf * mr / (mf + mr):.6f}")

domains = {r[0]: r[3] for r in csv.reader(open(D + "/data/afdb_families.tsv"), delimiter="\t")}
afdb = defaultdict(list)
per_domain = defaultdict(list)
families = set()
for family, tool, kind, score in csv.reader(open(D + "/data/afdb_scores.tsv"), delimiter="\t"):
	if kind != "lddt" or family in TRAIN:
		continue
	families.add(family)
	afdb[tool].append(float(score))
	per_domain[(tool, domains[family])].append(float(score))
print("AFDB families after removing training:", len(families))
for tool in sorted(afdb):
	print(f"AFDB {tool} {describe(afdb[tool])}")
for tool in ("foldmason", "foldmason_fast"):
	for nd in ("1", "2", "3", "4"):
		v = per_domain[(tool, nd)]
		print(f"AFDB {tool} domains={nd} n={len(v)} mean={st.mean(v):.6f}")

# Spread of each per-domain subset, used as tolerance for the Fig. 2B points
for tool in ("foldmason", "foldmason_fast"):
	for nd in ("1", "2", "3", "4"):
		print(f"AFDB {tool} domains={nd} {describe(per_domain[(tool, nd)])}")
