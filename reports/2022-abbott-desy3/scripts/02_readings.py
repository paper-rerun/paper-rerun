"""Tries several summary rules against the published numbers, to find the one they used.

The frozen rule (weighted mean with 16/84 percentiles) reproduces every central value but
misses the bounds wherever the marginal is skewed. This asks which rule reproduces the
bounds too. Nothing here moves the verdict: the frozen rule is scored in 03_score.py.

Usage: 02_readings.py <chain.txt> <out.json>
"""
import json
import sys

import numpy as np

CHAIN, OUT = sys.argv[1], sys.argv[2]

with open(CHAIN, encoding="utf-8") as fh:
	names = [h.strip().lower() for h in fh.readline().lstrip("#").rstrip("\n").split("\t")]
col = {n: i for i, n in enumerate(names)}
rows = np.loadtxt(CHAIN, comments="#")
w = rows[:, col["weight"]]
om = rows[:, col["cosmological_parameters--omega_m"]]
sig = rows[:, col["cosmological_parameters--sigma_8"]]
params = {"Omega_m": om, "sigma_8": sig, "S_8": sig * np.sqrt(om / 0.3),
	"h": rows[:, col["cosmological_parameters--h0"]]}
if "cosmological_parameters--w" in col:
	params["w"] = rows[:, col["cosmological_parameters--w"]]


def wq(x, q, weights):
	o = np.argsort(x)
	x, weights = x[o], weights[o]
	c = np.cumsum(weights) - 0.5 * weights
	c /= weights.sum()
	return np.interp(q, c, x)


def kde_grid(x, weights, n=512, bw_factor=1.0):
	# Gaussian KDE on a grid, weighted, Silverman bandwidth times a factor
	neff = weights.sum() ** 2 / (weights ** 2).sum()
	mean = np.average(x, weights=weights)
	std = np.sqrt(np.average((x - mean) ** 2, weights=weights))
	bw = bw_factor * 1.06 * std * neff ** (-0.2)
	lo, hi = x.min() - 3 * bw, x.max() + 3 * bw
	grid = np.linspace(lo, hi, n)
	dens = np.zeros(n)
	wn = weights / weights.sum()
	for xi, wi in zip(x, wn):
		dens += wi * np.exp(-0.5 * ((grid - xi) / bw) ** 2)
	dens /= np.trapezoid(dens, grid)
	return grid, dens


def hpd_from_density(grid, dens, area=0.68):
	# Highest-density interval: lower the threshold until the enclosed area reaches `area`
	order = np.argsort(dens)[::-1]
	cum = np.cumsum(dens[order])
	cum /= cum[-1]
	k = np.searchsorted(cum, area)
	thresh = dens[order][min(k, len(order) - 1)]
	inside = grid[dens >= thresh]
	return float(inside.min()), float(inside.max())


def cc_mean_bounds(grid, dens, area=0.68):
	# What ChainConsumer calls statistics='mean': cumulative density, symmetric in area
	cdf = np.cumsum(dens)
	cdf /= cdf[-1]
	lo = float(np.interp(0.5 - area / 2, cdf, grid))
	hi = float(np.interp(0.5 + area / 2, cdf, grid))
	return lo, hi


out = {"chain": CHAIN, "params": {}}
for name, x in params.items():
	mean = float(np.average(x, weights=w))
	q16, q50, q84 = [float(wq(x, q, w)) for q in (0.16, 0.5, 0.84)]
	grid, dens = kde_grid(x, w)
	hlo, hhi = hpd_from_density(grid, dens)
	kmax = float(grid[int(np.argmax(dens))])
	clo, chi = cc_mean_bounds(grid, dens)
	out["params"][name] = {
		"mean": mean, "median": q50, "kde_mode": kmax,
		"quantile_1684": [q16, q84],
		"hpd68_kde": [hlo, hhi],
		"cc_mean_kde": [clo, chi],
		"plus_minus": {
			"mean_quantile": [q84 - mean, mean - q16],
			"mean_hpd": [hhi - mean, mean - hlo],
			"median_hpd": [hhi - q50, q50 - hlo],
			"mode_hpd": [hhi - kmax, kmax - hlo],
			"mean_cc": [chi - mean, mean - clo],
			"median_cc": [chi - q50, q50 - clo],
		},
	}

open(OUT, "w", encoding="utf-8", newline="\n").write(json.dumps(out, indent=1))
print(json.dumps(out["params"], indent=1))
