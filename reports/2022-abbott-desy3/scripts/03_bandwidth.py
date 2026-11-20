"""How much the mean+HPD bounds move with the KDE bandwidth.

The authors' own plotting script calls ChainConsumer with kde=1.5, which scales the
bandwidth, so the bound they printed depends on that choice. This sweeps it.

Usage: 03_bandwidth.py <chain.txt> <out.json>
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

neff = w.sum() ** 2 / (w ** 2).sum()
out = {"chain": CHAIN, "neff": float(neff), "params": {}}
for name, x in params.items():
	mean = float(np.average(x, weights=w))
	std = float(np.sqrt(np.average((x - mean) ** 2, weights=w)))
	entry = {"mean": mean, "by_bandwidth": {}}
	for fac in (0.6, 0.8, 1.0, 1.2, 1.5, 2.0):
		bw = fac * 1.06 * std * neff ** (-0.2)
		grid = np.linspace(x.min() - 3 * bw, x.max() + 3 * bw, 2048)
		dens = np.zeros_like(grid)
		wn = w / w.sum()
		for xi, wi in zip(x, wn):
			dens += wi * np.exp(-0.5 * ((grid - xi) / bw) ** 2)
		order = np.argsort(dens)[::-1]
		cum = np.cumsum(dens[order]) / dens.sum()
		thresh = dens[order][min(int(np.searchsorted(cum, 0.68)), len(order) - 1)]
		inside = grid[dens >= thresh]
		entry["by_bandwidth"]["%.1f" % fac] = [float(inside.max() - mean), float(mean - inside.min())]
	out["params"][name] = entry

open(OUT, "w", encoding="utf-8", newline="\n").write(json.dumps(out, indent=1))
print(json.dumps(out["params"], indent=1))
