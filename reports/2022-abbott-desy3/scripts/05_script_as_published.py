"""Runs the authors' published reader on the file it names, and on the fiducial chain.

read_chains_y3a2.py takes sigma_8 at index 30 and the weight at index 36. This computes
S_8 that way and by the header, so the difference is visible as a number.

Usage: 05_script_as_published.py <chain.txt> <out.json>
"""
import json
import sys

import numpy as np

CHAIN, OUT = sys.argv[1], sys.argv[2]
with open(CHAIN, encoding="utf-8") as fh:
	names = [n.strip().lower() for n in fh.readline().lstrip("#").rstrip("\n").split("\t")]
col = {n: i for i, n in enumerate(names)}
rows = np.loadtxt(CHAIN, comments="#")

om = rows[:, col["cosmological_parameters--omega_m"]]
sig_header = rows[:, col["cosmological_parameters--sigma_8"]]
w_header = rows[:, col["weight"]]
sig_script = rows[:, 30]
w_script = rows[:, 36]


def summary(x, weights):
	mean = float(np.average(x, weights=weights))
	o = np.argsort(x)
	xs, ws = x[o], weights[o]
	c = (np.cumsum(ws) - 0.5 * ws) / ws.sum()
	return {"mean": mean, "q16": float(np.interp(0.16, c, xs)), "q84": float(np.interp(0.84, c, xs))}


out = {
	"chain": CHAIN,
	"n_columns": len(names),
	"index_30_is": names[30],
	"index_36_is": names[36],
	"S8_by_header": summary(sig_header * np.sqrt(om / 0.3), w_header),
	"S8_as_the_script_computes_it": summary(sig_script * np.sqrt(om / 0.3), np.abs(w_script)),
	"weight_column_the_script_uses": {
		"name": names[36],
		"min": float(w_script.min()), "max": float(w_script.max()),
		"negative_values": int((w_script < 0).sum()),
	},
}
open(OUT, "w", encoding="utf-8", newline="\n").write(json.dumps(out, indent=1))
print(json.dumps(out, indent=1))
