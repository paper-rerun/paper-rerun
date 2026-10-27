# Compare our AFDB LDDT with the authors' per-cluster scores and with claims.json (C5, C6, S6-S10)
# 285 of the 3,200 inputs are gone from AFDB, so the clusters are split in two:
#   complete (all 20 members, same sequences as the authors' MSA): per-cluster diff against afdb_scores.tsv
#   reduced (1 to 7 members missing): flagged, never compared to the authors' value for that cluster
# Any 160-cluster mean is printed as reduced-input, with no match / outside-tolerance verdict against C5/C6
# Usage: python3 -I compare.py <project root> [our scores tsv]
import csv
import json
import statistics as st
import sys

ROOT = sys.argv[1]
OURS = sys.argv[2] if len(sys.argv) > 2 else ROOT + "/runs/afdb/our_afdb_scores.tsv"
TOOLS = ("foldmason", "foldmason_fast")
claims = {c["id"]: c for c in json.load(open(ROOT + "/claims.json"))["claims"]}
domains = {r[0]: r[3] for r in csv.reader(open(ROOT + "/sources/analysis/data/afdb_families.tsv"), delimiter="\t")}

# Missing members per cluster, from the sequence check against the authors' MSA
missing = {}
for row in csv.DictReader(open(ROOT + "/runs/v4_vs_v6/sequence_check_per_cluster.tsv"), delimiter="\t"):
	assert row["seq_changed"] == "0", row
	missing[row["cluster"]] = int(row["missing"])
assert len(missing) == 160, len(missing)

def load(path):
	scores = {}
	for family, tool, kind, score in csv.reader(open(path), delimiter="\t"):
		if kind == "lddt" and tool in TOOLS:
			scores[(family, tool)] = float(score)
	return scores

ours = load(OURS)
theirs = load(ROOT + "/sources/analysis/data/afdb_scores.tsv")
complete = sorted(c for c in missing if missing[c] == 0 and (c, "foldmason") in ours)
reduced = sorted(c for c in missing if missing[c] > 0 and (c, "foldmason") in ours)
print(f"clusters with our scores: {len(complete)} complete, {len(reduced)} reduced inputs")

# (a) Complete clusters: same inputs as the authors, so a deterministic tool should match closely
print("\n(a) complete clusters, per-cluster diff against the authors' afdb_scores.tsv")
for tool in TOOLS:
	diffs = [ours[(c, tool)] - theirs[(c, tool)] for c in complete]
	exact = sum(abs(d) < 1e-6 for d in diffs)
	ours_mean = st.mean(ours[(c, tool)] for c in complete)
	theirs_mean = st.mean(theirs[(c, tool)] for c in complete)
	print(f"  {tool}: n={len(diffs)}  |diff|<1e-6 in {exact}  mean |diff| {st.mean(abs(d) for d in diffs):.4f}  max |diff| {max(abs(d) for d in diffs):.4f}  mean ours {ours_mean:.4f} authors {theirs_mean:.4f}")

# (b) Reduced clusters: listed, not compared per cluster
print("\n(b) reduced-input clusters (not the authors' inputs, no per-cluster comparison)")
print("  " + " ".join(f"{c}(-{missing[c]})" for c in reduced))

# (c) Means over everything we ran, labelled as reduced-input
print("\n(c) means over all clusters we ran: REDUCED-INPUT, not the pre-registered quantity, no verdict")
def show(label, values, paper):
	print(f"  {label}\tn={len(values)}\tours {st.mean(values):.4f}\tpre-registered {paper:.4f}\t(reduced-input, not comparable)")
run = complete + reduced
for tool, claim_id in (("foldmason", "C5"), ("foldmason_fast", "C6")):
	show(claim_id, [ours[(c, tool)] for c in run], claims[claim_id]["paper_value"])
for nd, claim_id in (("1", "S6"), ("2", "S7"), ("3", "S8"), ("4", "S9")):
	show(f"{claim_id} ({nd} dom)", [ours[(c, "foldmason")] for c in run if domains[c] == nd], claims[claim_id]["paper_value"])
for i, nd in enumerate(("1", "2", "3", "4")):
	show(f"S10[{nd} dom]", [ours[(c, "foldmason_fast")] for c in run if domains[c] == nd], claims["S10"]["paper_value"][i])

with open(ROOT + "/runs/afdb/per_cluster_diff.tsv", "w") as out:
	out.write("cluster\tdomains\tmissing\tinputs\ttool\tauthors\tours\tdiff\n")
	for c in run:
		inputs = "complete" if missing[c] == 0 else "reduced"
		for tool in TOOLS:
			out.write(f"{c}\t{domains[c]}\t{missing[c]}\t{inputs}\t{tool}\t{theirs[(c, tool)]:.6f}\t{ours[(c, tool)]:.6f}\t{ours[(c, tool)] - theirs[(c, tool)]:+.6f}\n")
