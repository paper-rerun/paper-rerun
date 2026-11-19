"""Puts the two files of the same deposit side by side, machine by machine.

Zenodo 10.5281/zenodo.7928362 holds both the table (the xlsx, one row per model per machine)
and the molecules those rows were supposed to summarise (the tsv.xz). If the table describes
that sample, then recomputing the ratios from the molecules has to give the printed values
back under some consistent reading. This checks every reading against both target models at
once and says which ones survive.

Reads the xlsx values sheet for the published per-machine numbers and runs/out/definitions.json
for the recomputed ones, so it does not touch the 496 MB file again.

Usage: 05_deposit_vs_deposit.py <xlsx> <definitions.json> <out.json>
"""
import json
import sys

import openpyxl

XLSX, DEFS, OUT = sys.argv[1], sys.argv[2], sys.argv[3]
TARGETS = {("ChEMBL 27", "LSTM RNN"): "sequence LSTM RNN",
	("ChEMBL 31", "GRU RNN"): "sequence GRU RNN"}

# What the xlsx prints, per machine
published = {}
wb = openpyxl.load_workbook(XLSX, data_only=True)
ws = wb["Values"]
rows = list(ws.iter_rows(values_only=True))
header = [str(c).strip() if c is not None else "" for c in rows[1]]
col = {name: i for i, name in enumerate(header)}
for row in rows[2:]:
	if row[0] is None:
		continue
	key = (str(row[col["dataset"]]).strip(), str(row[col["DrugEx version"]]).strip())
	if key not in TARGETS:
		continue
	machine = str(row[col["Machine"]]).strip()
	published["%s|%s|%s" % (machine, key[0], TARGETS[key])] = {
		"validity": float(row[col["validity"]]),
		"uniqueness": float(row[col["uniqueness"]]),
		"sample_size": int(row[col["sample size"]]),
		"batch_size": int(row[col["batch size"]]),
	}

recomputed = json.load(open(DEFS, encoding="utf-8"))

READINGS_VALIDITY = ["validity_their_flag", "validity_parseable", "validity_single_fragment"]
READINGS_UNIQUENESS = ["uniqueness_their_flag", "uniqueness_distinct_raw_over_n",
	"uniqueness_distinct_canonical_over_n", "uniqueness_distinct_canonical_over_valid"]

out = {"per_machine": {}, "readings_that_match_both_models": []}
for cell, pub in sorted(published.items()):
	got = recomputed.get(cell)
	if got is None:
		out["per_machine"][cell] = {"published": pub, "molecules_file": "not in the tsv"}
		continue
	out["per_machine"][cell] = {
		"published_validity": pub["validity"],
		"published_uniqueness": pub["uniqueness"],
		"sample_size_both": [pub["sample_size"], got["n"]],
		"batch_size_published": pub["batch_size"],
		"recomputed": {k: got[k] for k in READINGS_VALIDITY + READINGS_UNIQUENESS},
	}

# A reading survives only if it lands inside 1% of print on every machine of both models
for v in READINGS_VALIDITY:
	for u in READINGS_UNIQUENESS:
		ok = True
		for cell, pub in published.items():
			got = recomputed.get(cell)
			if got is None:
				continue
			if abs(got[v] - pub["validity"]) > 0.01 * pub["validity"]:
				ok = False
			if abs(got[u] - pub["uniqueness"]) > 0.01 * pub["uniqueness"]:
				ok = False
		if ok:
			out["readings_that_match_both_models"].append({"validity": v, "uniqueness": u})

open(OUT, "w", encoding="utf-8", newline="\n").write(json.dumps(out, indent=1))
print(json.dumps(out, indent=1))
