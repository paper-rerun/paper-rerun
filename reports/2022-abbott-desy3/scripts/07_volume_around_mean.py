"""Tests the literal reading of the paper's sentence, and where the printed interval sits.

Section V says the bound is "the 68% confidence limit of posterior volume around the mean".
Read literally that is 34% of the volume on each side of the mean. This computes that, and
also prints the absolute endpoints of the published interval, to see whether the printed
central value sits inside it symmetrically or not.

Usage: 07_volume_around_mean.py <chain.txt> <out.json>
"""
import json
import sys

import numpy as np

CHAIN, OUT = sys.argv[1], sys.argv[2]
with open(CHAIN, encoding="utf-8") as fh:
	names = [n.strip().lower() for n in fh.readline().lstrip("#").rstrip("\n").split("\t")]
col = {n: i for i, n in enumerate(names)}
rows = np.loadtxt(CHAIN, comments="#")
w = rows[:, col["weight"]]
om = rows[:, col["cosmological_parameters--omega_m"]]
sig = rows[:, col["cosmological_parameters--sigma_8"]]
params = {"Omega_m": om, "sigma_8": sig, "S_8": sig * np.sqrt(om / 0.3),
	"h": rows[:, col["cosmological_parameters--h0"]]}
if "cosmological_parameters--w" in col:
	params["w"] = rows[:, col["cosmological_parameters--w"]]


def wcdf(x, w):
	o = np.argsort(x)
	xs, ws = x[o], w[o]
	return xs, (np.cumsum(ws) - 0.5 * ws) / ws.sum()


def hpd(x, w, area=0.68, n=2048):
	neff = w.sum() ** 2 / (w ** 2).sum()
	mean = np.average(x, weights=w)
	std = np.sqrt(np.average((x - mean) ** 2, weights=w))
	bw = 1.06 * std * neff ** (-0.2)
	grid = np.linspace(x.min() - 3 * bw, x.max() + 3 * bw, n)
	dens = np.zeros(n)
	wn = w / w.sum()
	for xi, wi in zip(x, wn):
		dens += wi * np.exp(-0.5 * ((grid - xi) / bw) ** 2)
	order = np.argsort(dens)[::-1]
	cum = np.cumsum(dens[order]) / dens.sum()
	thresh = dens[order][min(int(np.searchsorted(cum, area)), n - 1)]
	inside = grid[dens >= thresh]
	return float(inside.min()), float(inside.max())


out = {"chain": CHAIN, "params": {}}
for name, x in params.items():
	mean = float(np.average(x, weights=w))
	xs, c = wcdf(x, w)
	at_mean = float(np.interp(mean, xs, c))
	# Literal reading: 34% of the volume on each side of the mean
	lit_lo = float(np.interp(max(at_mean - 0.34, 0.0), c, xs))
	lit_hi = float(np.interp(min(at_mean + 0.34, 1.0), c, xs))
	lo, hi = hpd(x, w)
	out["params"][name] = {
		"mean": mean,
		"cdf_at_mean": at_mean,
		"volume_around_mean_34_each_side": {"plus": lit_hi - mean, "minus": mean - lit_lo},
		"hpd68": {"low": lo, "high": hi, "plus": hi - mean, "minus": mean - lo,
			"mean_is_at_fraction_of_interval": (mean - lo) / (hi - lo)},
	}

open(OUT, "w", encoding="utf-8", newline="\n").write(json.dumps(out, indent=1))
print(json.dumps(out["params"], indent=1))
