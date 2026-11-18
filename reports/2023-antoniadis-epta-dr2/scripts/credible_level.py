"""Table A.1's bounds are far wider in our recount than in print, on all eight. Test whether
that table is quoting a 68% region under a caption that says 90%.

For each cell, find the equal-tailed credible level whose bounds best match what is printed,
and compare the 90% and 68% readings side by side.
"""
import io, os, zipfile, tarfile, json
import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
Z = zipfile.ZipFile(os.path.join(ROOT, "data", "chains.zip"))

CELLS = [
    ("DR2full",  "hd_pl",  "gamma",   (4.19, 0.73, 0.63),  "Table 2"),
    ("DR2full",  "crn_pl", "gamma",   (4.13, 0.80, 0.59),  "Table 2"),
    ("DR2new",   "hd_pl",  "gamma",   (2.71, 1.18, 0.71),  "Table 2"),
    ("DR2new",   "bin_b10_orf", "gamma", (2.63, 0.86, 0.71), "Table 2 ORF"),
    ("DR2new",   "chebyshev_orf", "gamma", (2.57, 0.86, 0.76), "Table 2 ORF"),
    ("DR2full+", "crn_pl", "log10_A", (-14.44, 0.17, 0.20), "Table A.1"),
    ("DR2full+", "crn_pl", "gamma",   (3.98, 0.40, 0.37),  "Table A.1"),
    ("DR2full+", "hd_pl",  "log10_A", (-14.48, 0.18, 0.20), "Table A.1"),
    ("DR2full+", "hd_pl",  "gamma",   (4.06, 0.39, 0.40),  "Table A.1"),
    ("DR2new+",  "crn_pl", "log10_A", (-14.30, 0.33, 0.52), "Table A.1"),
    ("DR2new+",  "crn_pl", "gamma",   (3.53, 1.12, 0.84),  "Table A.1"),
    ("DR2new+",  "hd_pl",  "log10_A", (-14.10, 0.25, 0.44), "Table A.1"),
    ("DR2new+",  "hd_pl",  "gamma",   (3.03, 1.02, 0.67),  "Table A.1"),
]


def load(dataset, name):
    t = tarfile.open(fileobj=io.BytesIO(Z.read("chains/%s/%s.tar.gz" % (dataset, name))), mode="r:gz")
    pars = chain = None
    for n in t.getnames():
        if n.endswith("pars.txt"):
            pars = t.extractfile(n).read().decode().split()
        elif n.endswith("chain_1.txt"):
            chain = np.loadtxt(t.extractfile(n))
    t.close()
    return pars, chain


out, rows = [], []
cache = {}
for dataset, fname, short, tgt, where in CELLS:
    key = (dataset, fname)
    if key not in cache:
        cache[key] = load(dataset, fname)
    pars, arr = cache[key]
    col = pars.index([p for p in pars if p.startswith("gw") and p.endswith("_" + short)][0])
    x = arr[arr.shape[0] // 4:, col]
    med = float(np.median(x))

    def bounds(level):
        lo, hi = np.percentile(x, [50 - level / 2.0, 50 + level / 2.0])
        return float(hi - med), float(med - lo)

    best, best_err = None, 1e9
    for level in np.arange(50.0, 99.01, 0.25):
        p, m = bounds(level)
        err = abs(p - tgt[1]) + abs(m - tgt[2])
        if err < best_err:
            best, best_err = level, err
    p90, m90 = bounds(90.0)
    p68, m68 = bounds(68.0)
    rows.append({"dataset": dataset, "chain": fname, "param": short, "where": where,
                 "paper": list(tgt), "at90": [p90, m90], "at68": [p68, m68],
                 "best_level": float(best), "best_err": float(best_err)})
    out.append("%-9s %-14s %-8s %-12s artigo +%.2f -%.2f | 90%% +%.3f -%.3f | 68%% +%.3f -%.3f | melhor nivel %.1f%% (erro %.3f)"
               % (dataset, fname, short, where, tgt[1], tgt[2], p90, m90, p68, m68, best, best_err))

out.append("")
for where in ("Table 2", "Table 2 ORF", "Table A.1"):
    lv = [r["best_level"] for r in rows if r["where"] == where]
    if lv:
        out.append("%-12s nivel que melhor casa: mediana %.1f%%, faixa %.1f a %.1f%%"
                   % (where, float(np.median(lv)), min(lv), max(lv)))
txt = "\n".join(out) + "\n"
io.open(os.path.join(ROOT, "runs", "logs", "credible_level.log"), "w", encoding="utf-8", newline="\n").write(txt)
io.open(os.path.join(ROOT, "runs", "out", "credible_level.json"), "w", encoding="utf-8", newline="\n").write(json.dumps(rows, indent=1) + "\n")
print(txt)
