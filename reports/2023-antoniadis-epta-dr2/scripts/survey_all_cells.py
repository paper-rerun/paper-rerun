"""Every ENTERPRISE cell of Table 2 and Table A.1 that the release allows.

The frozen claims covered three cells. The adversarial review pointed out that the release
supports many more, and that the three we picked were the quiet corner of it. This runs all
of them: Table 2 (DR2full, DR2new) and Table A.1 (DR2full+, DR2new+).

Published values are transcribed from the arXiv LaTeX source of 2306.16214, tabulars
tab:pl and tab:pl_inpta, where the sub- and superscripts are unambiguous.
"""
import io, os, zipfile, tarfile, json
import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
Z = zipfile.ZipFile(os.path.join(ROOT, "data", "chains.zip"))

# (dataset, chain file) -> (row label, log10A triple, gamma triple), triples are (median, +, -)
CELLS = [
    ("DR2full",  "crn_pl",        "ENTERPRISE + CURN",         (-14.53, 0.29, 0.44), (4.13, 0.80, 0.59)),
    ("DR2full",  "hd_pl",         "ENTERPRISE + GWB",          (-14.54, 0.28, 0.41), (4.19, 0.73, 0.63)),
    ("DR2full",  "bin_b10_orf",   "ENTERPRISE + Binned ORF",   (-14.47, 0.27, 0.35), (4.10, 0.64, 0.56)),
    ("DR2full",  "chebyshev_orf", "ENTERPRISE + Chebyshev ORF",(-14.50, 0.32, 0.40), (4.17, 0.73, 0.72)),
    ("DR2full",  "legendre_orf",  "ENTERPRISE + Legendre ORF", (-14.51, 0.30, 0.40), (4.19, 0.74, 0.63)),
    ("DR2new",   "crn_pl",        "ENTERPRISE + CURN",         (-14.00, 0.28, 0.77), (2.91, 1.72, 0.87)),
    ("DR2new",   "hd_pl",         "ENTERPRISE + GWB",          (-13.94, 0.23, 0.48), (2.71, 1.18, 0.71)),
    ("DR2new",   "bin_b10_orf",   "ENTERPRISE + Binned ORF",   (-13.89, 0.22, 0.32), (2.63, 0.86, 0.71)),
    ("DR2new",   "chebyshev_orf", "ENTERPRISE + Chebyshev ORF",(-13.87, 0.22, 0.31), (2.57, 0.86, 0.76)),
    ("DR2new",   "legendre_orf",  "ENTERPRISE + Legendre ORF", (-13.89, 0.23, 0.35), (2.59, 0.98, 0.72)),
    ("DR2full+", "crn_pl",        "ENTERPRISE + CURN (A.1)",   (-14.44, 0.17, 0.20), (3.98, 0.40, 0.37)),
    ("DR2full+", "hd_pl",         "ENTERPRISE + GWB (A.1)",    (-14.48, 0.18, 0.20), (4.06, 0.39, 0.40)),
    ("DR2new+",  "crn_pl",        "ENTERPRISE + CURN (A.1)",   (-14.30, 0.33, 0.52), (3.53, 1.12, 0.84)),
    ("DR2new+",  "hd_pl",         "ENTERPRISE + GWB (A.1)",    (-14.10, 0.25, 0.44), (3.03, 1.02, 0.67)),
]

TOL_MED, TOL_BOUND = 0.01, 0.02


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


rows, out = [], []
bad_med = bad_bound = total = 0
for dataset, fname, label, tA, tG in CELLS:
    pars, arr = load(dataset, fname)
    burn = arr.shape[0] // 4
    rec = {"dataset": dataset, "chain": fname, "row": label, "n": int(arr.shape[0])}
    out.append("%-9s %-14s -> %-28s n=%d" % (dataset, fname, label, arr.shape[0]))
    for short, tgt in (("log10_A", tA), ("gamma", tG)):
        cand = [p for p in pars if p.startswith("gw") and p.endswith("_" + short)]
        if len(cand) != 1:
            out.append("    %-8s %d candidatos, pulado" % (short, len(cand)))
            continue
        x = arr[burn:, pars.index(cand[0])]
        med = float(np.median(x))
        p5, p95 = (float(v) for v in np.percentile(x, [5, 95]))
        dm, dp, dmi = med - tgt[0], (p95 - med) - tgt[1], (med - p5) - tgt[2]
        total += 3
        bad_med += abs(dm) > TOL_MED
        bad_bound += (abs(dp) > TOL_BOUND) + (abs(dmi) > TOL_BOUND)
        rec[short] = {"param": cand[0], "ours": [med, p95 - med, med - p5],
                      "paper": list(tgt), "delta": [dm, dp, dmi]}
        out.append("    %-8s %+.4f +%.4f -%.4f | artigo %+.2f +%.2f -%.2f | d %+.4f %+.4f %+.4f%s"
                   % (short, med, p95 - med, med - p5, tgt[0], tgt[1], tgt[2], dm, dp, dmi,
                      "" if abs(dm) <= TOL_MED and abs(dp) <= TOL_BOUND and abs(dmi) <= TOL_BOUND else "   <<"))
    rows.append(rec)

out.append("")
out.append("%d numeros ao todo: %d medianas fora de %.2f, %d bordas fora de %.2f"
           % (total, bad_med, TOL_MED, bad_bound, TOL_BOUND))
txt = "\n".join(out) + "\n"
io.open(os.path.join(ROOT, "runs", "logs", "survey_all_cells.log"), "w", encoding="utf-8", newline="\n").write(txt)
io.open(os.path.join(ROOT, "runs", "out", "survey_all_cells.json"), "w", encoding="utf-8", newline="\n").write(json.dumps(rows, indent=1) + "\n")
print(txt)
