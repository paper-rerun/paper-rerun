"""Scores the run against the frozen rule, and against the rule the paper describes.

The frozen rule is the weighted mean with the 16th and 84th weighted percentiles. The paper
says "68% confidence limit of posterior volume around the mean", which is not the same thing
whenever the marginal is skewed, so the second rule is the 68% highest-density interval of
the weighted KDE, with the mean as the central value. Both are reported; the verdict is the
frozen one.

Usage: 06_score.py <claims.json> <claims.sha256> <out.json>
"""
import hashlib
import json
import sys

import numpy as np

CLAIMS, SHA, OUT = sys.argv[1], sys.argv[2], sys.argv[3]
digest = hashlib.sha256(open(CLAIMS, "rb").read()).hexdigest()
if digest != open(SHA, encoding="utf-8").read().split()[0]:
	sys.exit("claims.json changed after freezing")
claims = json.load(open(CLAIMS, encoding="utf-8"))

CHAINS = {}


def load(path):
	if path in CHAINS:
		return CHAINS[path]
	with open(path, encoding="utf-8") as fh:
		names = [n.strip().lower() for n in fh.readline().lstrip("#").rstrip("\n").split("\t")]
	col = {n: i for i, n in enumerate(names)}
	rows = np.loadtxt(path, comments="#")
	w = rows[:, col["weight"]]
	om = rows[:, col["cosmological_parameters--omega_m"]]
	sig = rows[:, col["cosmological_parameters--sigma_8"]]
	p = {"Omega_m": om, "sigma_8": sig, "S_8": sig * np.sqrt(om / 0.3),
		"h": rows[:, col["cosmological_parameters--h0"]]}
	if "cosmological_parameters--w" in col:
		p["w"] = rows[:, col["cosmological_parameters--w"]]
	CHAINS[path] = (p, w)
	return CHAINS[path]


def wq(x, q, w):
	o = np.argsort(x)
	x, w = x[o], w[o]
	c = (np.cumsum(w) - 0.5 * w) / w.sum()
	return float(np.interp(q, c, x))


def hpd(x, w, area=0.68, n=2048):
	# 68% highest-density interval of the weighted Gaussian KDE, Silverman bandwidth
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


rows = []
for c in claims["claims"]:
	p, w = load("downloads/" + c["chain"])
	x = p[c["param"]]
	mean = float(np.average(x, weights=w))
	q16, q84 = wq(x, 0.16, w), wq(x, 0.84, w)
	lo, hi = hpd(x, w)
	two = c["param"] == "w"
	tol_c = 0.005 if two else 0.001
	tol_b = 0.01 if two else 0.002
	frozen = {"central": mean, "plus": q84 - mean, "minus": mean - q16}
	paper = {"central": mean, "plus": hi - mean, "minus": mean - lo}
	def verdict(d):
		return {"central_ok": abs(d["central"] - c["value"]) <= tol_c,
			"plus_ok": abs(d["plus"] - c["plus"]) <= tol_b,
			"minus_ok": abs(d["minus"] - c["minus"]) <= tol_b}
	rows.append({"id": c["id"], "param": c["param"], "chain": c["chain"],
		"published": {"value": c["value"], "plus": c["plus"], "minus": c["minus"]},
		"frozen_rule": frozen | verdict(frozen),
		"paper_rule_hpd": paper | verdict(paper)})

def tally(key):
	ok_c = sum(r[key]["central_ok"] for r in rows)
	ok_all = sum(all(r[key][k] for k in ("central_ok", "plus_ok", "minus_ok")) for r in rows)
	return {"central_only": ok_c, "central_and_both_bounds": ok_all, "of": len(rows)}

summary = {"claims_hash": digest, "frozen": tally("frozen_rule"),
	"paper_rule_hpd": tally("paper_rule_hpd"), "rows": rows}
t = summary["frozen"]
summary["verdict_frozen_rule"] = ("Reproduced" if t["central_and_both_bounds"] == t["of"]
	else "Not reproduced" if t["central_only"] == 0 else "Partially reproduced")
open(OUT, "w", encoding="utf-8", newline="\n").write(json.dumps(summary, indent=1))

print("| claim | param | published | frozen rule (mean, 16/84) | paper rule (mean, HPD 68%) |")
print("|---|---|---|---|---|")
for r in rows:
	p = r["published"]
	f, h = r["frozen_rule"], r["paper_rule_hpd"]
	mark = lambda d: "ok" if all(d[k] for k in ("central_ok", "plus_ok", "minus_ok")) else "**fails**"
	print("| %s | %s | %.3f +%.3f -%.3f | %.4f +%.4f -%.4f %s | %.4f +%.4f -%.4f %s |" % (
		r["id"], r["param"], p["value"], p["plus"], p["minus"],
		f["central"], f["plus"], f["minus"], mark(f),
		h["central"], h["plus"], h["minus"], mark(h)))
print("\nfrozen: %s" % json.dumps(summary["frozen"]))
print("paper rule: %s" % json.dumps(summary["paper_rule_hpd"]))
print("verdict (frozen): %s" % summary["verdict_frozen_rule"])
