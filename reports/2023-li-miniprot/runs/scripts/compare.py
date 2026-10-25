# Compare the main run with the pre-registered claims and tabulate the alternative readings.
# Usage: python3 -I compare.py <root>
import json
import os
import re
import sys

ROOT = sys.argv[1]
COLUMNS = ["zf_hs_j2", "zf_hs_j1", "mm_hs_j2", "ag_dm_j2"]
QUERY_OF = {"zf_hs_j2": "zebrafish.longest.faa", "zf_hs_j1": "zebrafish.longest.faa", "mm_hs_j2": "mouse.testset.faa", "ag_dm_j2": "mosquito.longest.faa"}


def parse_outputs(prefix):
	values = {}
	junc_path = prefix + ".junceval.txt"
	if os.path.exists(junc_path):
		text = open(junc_path).read()
		mapped = int(re.search(r"# mapped reads: (\d+)", text).group(1))
		singletons = int(re.search(r"# singletons: (\d+)", text).group(1))
		values["mapped"] = mapped
		values["single_exon"] = singletons
		values["n_multi_exon"] = mapped - singletons
		values["n_pred_junc"] = int(re.search(r"# predicted introns: (\d+)", text).group(1))
		values["n_nonovlp_junc"] = int(re.search(r"# non-overlapping introns: (\d+)", text).group(1))
		correct = re.search(r"# correct introns: (\d+) \(([\d.]+)%\)", text)
		values["n_confirmed_junc"] = int(correct.group(1))
		values["pct_confirmed_junc"] = float(correct.group(2))
	exon_path = prefix + ".exoneval.txt"
	if os.path.exists(exon_path):
		text = open(exon_path).read()
		sn = re.search(r"Base Sn: \d+ / \d+ = ([\d.]+)%", text)
		sp = re.search(r"Base Sp: \d+ / \d+ = ([\d.]+)%", text)
		if sn:
			values["pct_base_sn"] = float(sn.group(1))
			values["pct_base_sp"] = float(sp.group(1))
	return values


def count_fasta(path):
	return sum(1 for line in open(path) if line.startswith(">"))


def check(claim, ours):
	paper = claim["paper_value"]
	tolerance = claim["tolerance"]
	if tolerance.startswith("reported exactly"):
		return None
	if "percentage points" in tolerance:
		limit = float(re.search(r"<= ([\d.]+) percentage", tolerance).group(1))
		return abs(ours - paper) <= limit + 1e-9
	limit = float(re.search(r"<= ([\d.]+)%", tolerance).group(1))
	return abs(ours - paper) / paper * 100 <= limit + 1e-9


def main():
	claims = json.load(open(ROOT + "/claims.json", encoding="utf-8"))
	results = {}
	for column in COLUMNS:
		values = parse_outputs(ROOT + "/runs/main/" + column)
		values["n_proteins"] = count_fasta(ROOT + "/runs/testsets/" + QUERY_OF[column])
		results[column] = values

	rows = []
	for claim in claims["claims"]:
		column, key = claim["id"].split(".")
		ours = results[column].get(key)
		passed = check(claim, ours) if ours is not None else None
		diff = None if ours is None else round(ours - claim["paper_value"], 4)
		rows.append({"id": claim["id"], "role": claim["role"], "paper": claim["paper_value"], "ours": ours, "diff": diff, "tolerance": claim["tolerance"], "within": passed})

	primary = [row for row in rows if row["role"] == "primary"]
	n_within = sum(1 for row in primary if row["within"])
	if n_within == len(primary):
		verdict = "Reproduced"
	elif n_within == 0:
		verdict = "Not reproduced"
	else:
		verdict = "Partially reproduced"

	summary = {"verdict": verdict, "primary_within": n_within, "primary_total": len(primary), "rows": rows, "main_values": results}

	# Alternative readings
	alt = {}
	alt_dir = ROOT + "/runs/alt"
	if os.path.isdir(alt_dir):
		labels = sorted(set(re.sub(r"\.(junceval|exoneval)\.txt$", "", name) for name in os.listdir(alt_dir) if name.endswith("eval.txt")))
		for label in labels:
			values = parse_outputs(alt_dir + "/" + label)
			match = re.search(r"ALT-(zf_\w+|mm_\w+)$", label)
			if match:
				values["n_proteins"] = count_fasta(ROOT + "/runs/testsets/alt/" + match.group(1) + ".faa")
			alt[label] = values
	summary["alt"] = alt

	json.dump(summary, open(ROOT + "/runs/results.json", "w"), indent=1)
	print("verdict:", verdict, n_within, "/", len(primary))
	for row in rows:
		print(row["id"], row["paper"], row["ours"], row["diff"], row["within"])
	for label, values in alt.items():
		print(label, values)


if __name__ == "__main__":
	main()
