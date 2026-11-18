"""Recount the EPTA DR2 III posterior summaries from the chains the authors published.

One chain per claim. PTMCMCSampler writes the sampled parameters first, in the order of
pars.txt, then four extra columns (lnpost, lnlike, acceptance, PT swap). We read each
parameter by its exact name in pars.txt, never by column index, because every pulsar in
the model also has a parameter whose name ends in log10_A.

The paper quotes 90% credible regions as a median with an upper and a lower bound, so we
report the median and the 5th and 95th percentiles.
"""
import io, json, os
import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EXTRACTED = os.path.join(ROOT, "data", "extracted")

# claim id -> (chain dir, parameter prefix, what the paper calls it)
CASES = {
    "C1": ("DR2full__hd_pl/hd_pl", "gw_hd", "ENTERPRISE + GWB, DR2full"),
    "C2": ("DR2new__hd_pl/hd_pl", "gw_hd", "ENTERPRISE + GWB, DR2new"),
    "C3": ("DR2full__crn_pl/crn_pl", "gw_crn", "ENTERPRISE + CURN, DR2full"),
}

TARGETS = {
    "C1": {"log10_A": (-14.54, 0.28, 0.41), "gamma": (4.19, 0.73, 0.63)},
    "C2": {"log10_A": (-13.94, 0.23, 0.48), "gamma": (2.71, 1.18, 0.71)},
    "C3": {"log10_A": (-14.53, 0.29, 0.44), "gamma": (4.13, 0.80, 0.59)},
}

TOL_MEDIAN = 0.01
TOL_BOUND = 0.02


def summarise(x):
    med = float(np.median(x))
    lo, hi = (float(v) for v in np.percentile(x, [5.0, 95.0]))
    return {"median": med, "plus": hi - med, "minus": med - lo, "p5": lo, "p95": hi}


def stationarity(x):
    """Crude check that the chain is already burnt in: compare the first and last tenth."""
    n = len(x)
    a, b = x[: n // 10], x[-(n // 10):]
    return {"median_first_tenth": float(np.median(a)),
            "median_last_tenth": float(np.median(b)),
            "delta": float(np.median(b) - np.median(a))}


results = {"tolerance": {"median": TOL_MEDIAN, "bound": TOL_BOUND}, "cases": {}}

for cid, (sub, prefix, label) in CASES.items():
    d = os.path.join(EXTRACTED, sub)
    pars = [l.strip() for l in io.open(os.path.join(d, "pars.txt")) if l.strip()]
    arr = np.loadtxt(os.path.join(d, "chain_1.txt"))
    n_all = arr.shape[0]

    entry = {"label": label, "dir": sub, "n_samples": int(n_all),
             "n_params": len(pars), "n_columns": int(arr.shape[1]),
             "extra_columns": int(arr.shape[1] - len(pars)), "params": {}}

    for short in ("log10_A", "gamma"):
        name = prefix + "_" + short
        if name not in pars:
            entry["params"][short] = {"erro": "parametro %s nao esta no pars.txt" % name}
            continue
        col = pars.index(name)
        x_all = arr[:, col]
        burn = n_all // 4
        frozen = summarise(x_all[burn:])          # the rule as frozen: drop the first 25%
        full = summarise(x_all)                   # sensitivity: keep everything
        tgt_med, tgt_plus, tgt_minus = TARGETS[cid][short]
        entry["params"][short] = {
            "param_name": name,
            "column": col,
            "n_post_burn": int(n_all - burn),
            "frozen_rule_burn25": frozen,
            "no_burn_in": full,
            "stationarity_first_vs_last_tenth": stationarity(x_all),
            "paper": {"median": tgt_med, "plus": tgt_plus, "minus": tgt_minus},
            "delta_median": frozen["median"] - tgt_med,
            "delta_plus": frozen["plus"] - tgt_plus,
            "delta_minus": frozen["minus"] - tgt_minus,
            "pass_median": abs(frozen["median"] - tgt_med) <= TOL_MEDIAN,
            "pass_plus": abs(frozen["plus"] - tgt_plus) <= TOL_BOUND,
            "pass_minus": abs(frozen["minus"] - tgt_minus) <= TOL_BOUND,
        }
    results["cases"][cid] = entry

io.open(os.path.join(ROOT, "runs", "out", "results.json"), "w", encoding="utf-8",
        newline="\n").write(json.dumps(results, indent=1) + "\n")

lines = []
for cid, e in results["cases"].items():
    lines.append("%s  %s  (%d amostras, %d parametros + %d colunas extras)"
                 % (cid, e["label"], e["n_samples"], e["n_params"], e["extra_columns"]))
    for short, p in e["params"].items():
        if "erro" in p:
            lines.append("   %-8s %s" % (short, p["erro"]))
            continue
        f = p["frozen_rule_burn25"]
        t = p["paper"]
        lines.append("   %-8s nosso %+.4f +%.4f -%.4f | artigo %+.2f +%.2f -%.2f"
                     % (short, f["median"], f["plus"], f["minus"],
                        t["median"], t["plus"], t["minus"]))
        lines.append("            delta  med %+.4f  mais %+.4f  menos %+.4f   -> %s %s %s"
                     % (p["delta_median"], p["delta_plus"], p["delta_minus"],
                        "ok" if p["pass_median"] else "FALHA",
                        "ok" if p["pass_plus"] else "FALHA",
                        "ok" if p["pass_minus"] else "FALHA"))
        g = p["no_burn_in"]
        s = p["stationarity_first_vs_last_tenth"]
        lines.append("            sem burn-in: med %+.4f +%.4f -%.4f | 1o decimo %+.4f vs ultimo %+.4f (d %+.4f)"
                     % (g["median"], g["plus"], g["minus"],
                        s["median_first_tenth"], s["median_last_tenth"], s["delta"]))
txt = "\n".join(lines) + "\n"
io.open(os.path.join(ROOT, "runs", "logs", "recount.log"), "w", encoding="utf-8",
        newline="\n").write(txt)
print(txt)
