"""Tests the blind run's thesis: the published validity column is the non-empty share.

The blind recount found that Table S4's validity for the RNN rows matches, not the fraction
of strings that parse, but the fraction of sampled sequences that decoded to a non-empty
string at all. This counts that share per machine over every RNN row of the deposit and puts
it beside what the xlsx prints, so the claim stands or falls on the authors' own data.

Usage: 08_nonempty.py <tsv.xz> <xlsx> <out.json>
"""
import collections
import json
import lzma
import sys

import openpyxl

TSV, XLSX, OUT = sys.argv[1], sys.argv[2], sys.argv[3]

rows = collections.Counter()
nonempty = collections.Counter()
valid_flag = collections.Counter()
with lzma.open(TSV, "rt", encoding="utf-8") as fh:
	header = fh.readline().rstrip("\n").split("\t")
	col = {name: i for i, name in enumerate(header)}
	for line in fh:
		f = line.rstrip("\n").split("\t")
		if len(f) != len(header):
			continue
		key = (f[col["dataset"]], f[col["DrugEx version"]], f[col["Machine"]])
		rows[key] += 1
		if f[col["SMILES"]].strip():
			nonempty[key] += 1
		if f[col["Valid"]] == "1.0":
			valid_flag[key] += 1

# What the xlsx prints for the same cells
published = {}
ws = openpyxl.load_workbook(XLSX, data_only=True)["Values"]
xr = list(ws.iter_rows(values_only=True))
xh = [str(c).strip() if c is not None else "" for c in xr[1]]
xc = {name: i for i, name in enumerate(xh)}
for row in xr[2:]:
	if row[0] is None:
		continue
	key = (str(row[xc["dataset"]]).strip(), str(row[xc["DrugEx version"]]).strip(),
		str(row[xc["Machine"]]).strip())
	published[key] = {"validity": float(row[xc["validity"]]),
		"uniqueness": float(row[xc["uniqueness"]])}

# The xlsx names the model "LSTM RNN", the molecules file "sequence LSTM RNN"
ALIAS = {"sequence LSTM RNN": "LSTM RNN", "sequence GRU RNN": "GRU RNN"}

out = {"per_row": {}, "rnn_rows": 0, "rnn_rows_matching_nonempty": 0}
for key in sorted(rows):
	dataset, version, machine = key
	if version not in ALIAS:
		continue
	pub = published.get((dataset, ALIAS[version], machine))
	n = rows[key]
	share = nonempty[key] / n
	entry = {"n": n, "nonempty": nonempty[key], "nonempty_share": share,
		"their_valid_flag_share": valid_flag[key] / n}
	if pub:
		entry["published_validity"] = pub["validity"]
		# The table prints three decimals, so round before comparing
		entry["nonempty_rounds_to_published"] = round(share, 3) == pub["validity"]
		out["rnn_rows"] += 1
		out["rnn_rows_matching_nonempty"] += entry["nonempty_rounds_to_published"]
	out["per_row"]["%s|%s|%s" % (dataset, version, machine)] = entry

open(OUT, "w", encoding="utf-8", newline="\n").write(json.dumps(out, indent=1))
print(json.dumps(out, indent=1))
