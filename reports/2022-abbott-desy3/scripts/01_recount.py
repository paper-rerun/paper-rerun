"""Recounts the published posterior summaries from the DES Y3 chains.

Reads each chain by its own header line, never by a fixed column index, because the
authors' own read_chains_y3a2.py hardcodes sigma_8 at index 30 and the weight at 36,
which is one column short of these files.

S_8 is formed the way their script forms it: sigma_8 * sqrt(omega_m / 0.3).

Usage: 01_recount.py <chain.txt> <out.json>
"""
import json
import sys

import numpy as np

CHAIN, OUT = sys.argv[1], sys.argv[2]

with open(CHAIN, encoding="utf-8") as fh:
	header = fh.readline().lstrip("#").rstrip("\n").split("\t")
names = [h.strip().lower() for h in header]
col = {n: i for i, n in enumerate(names)}

rows = np.loadtxt(CHAIN, comments="#")
if rows.shape[1] != len(names):
	sys.exit("header says %d columns, data has %d" % (len(names), rows.shape[1]))

w = rows[:, col["weight"]]
om = rows[:, col["cosmological_parameters--omega_m"]]
s8sigma = rows[:, col["cosmological_parameters--sigma_8"]]
params = {
	"Omega_m": om,
	"sigma_8": s8sigma,
	"S_8": s8sigma * np.sqrt(om / 0.3),
}
if "cosmological_parameters--h0" in col:
	params["h"] = rows[:, col["cosmological_parameters--h0"]]
if "cosmological_parameters--w" in col:
	params["w"] = rows[:, col["cosmological_parameters--w"]]


def wquantile(x, q, weights):
	# Weighted quantile: sort, walk the normalised cumulative weight, interpolate
	order = np.argsort(x)
	x, weights = x[order], weights[order]
	cum = np.cumsum(weights) - 0.5 * weights
	cum /= weights.sum()
	return np.interp(q, cum, x)


out = {"chain": CHAIN, "n_samples": int(rows.shape[0]),
	"weight_sum": float(w.sum()),
	"effective_samples": float(w.sum() ** 2 / (w ** 2).sum()),
	"columns": len(names), "params": {}}
for name, x in params.items():
	mean = float(np.average(x, weights=w))
	q16, q50, q84 = [float(wquantile(x, q, w)) for q in (0.16, 0.5, 0.84)]
	out["params"][name] = {
		"frozen_mean": mean,
		"frozen_plus": q84 - mean,
		"frozen_minus": mean - q16,
		"secondary_median": q50,
		"secondary_median_plus": q84 - q50,
		"secondary_median_minus": q50 - q16,
		"q16": q16, "q84": q84,
		"std": float(np.sqrt(np.average((x - mean) ** 2, weights=w))),
	}

open(OUT, "w", encoding="utf-8", newline="\n").write(json.dumps(out, indent=1))
print(json.dumps(out, indent=1))
