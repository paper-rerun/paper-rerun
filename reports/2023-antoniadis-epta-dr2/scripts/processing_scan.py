"""Where does the 0.0222 on the lower bound of gamma in DR2new come from?

We resample the very chain the authors published, so a difference cannot be sampler noise:
the samples are the same. It has to be a processing choice. Scan the two that exist:
how much burn-in is dropped, and which interpolation numpy uses for the percentile.
"""
import io, os
import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EXTRACTED = os.path.join(ROOT, "data", "extracted")
METHODS = ["linear", "lower", "higher", "nearest", "midpoint",
           "inverted_cdf", "averaged_inverted_cdf", "closest_observation",
           "interpolated_inverted_cdf", "hazen", "weibull", "median_unbiased",
           "normal_unbiased"]

CASES = {
    "C1 log10_A": ("DR2full__hd_pl/hd_pl", "gw_hd_log10_A", -14.54, 0.28, 0.41),
    "C1 gamma":   ("DR2full__hd_pl/hd_pl", "gw_hd_gamma", 4.19, 0.73, 0.63),
    "C2 log10_A": ("DR2new__hd_pl/hd_pl", "gw_hd_log10_A", -13.94, 0.23, 0.48),
    "C2 gamma":   ("DR2new__hd_pl/hd_pl", "gw_hd_gamma", 2.71, 1.18, 0.71),
    "C3 log10_A": ("DR2full__crn_pl/crn_pl", "gw_crn_log10_A", -14.53, 0.29, 0.44),
    "C3 gamma":   ("DR2full__crn_pl/crn_pl", "gw_crn_gamma", 4.13, 0.80, 0.59),
}

lines = []

# 1. burn-in scan, on the one number that misses
sub, par, tm, tp, tmi = CASES["C2 gamma"]
pars = [l.strip() for l in io.open(os.path.join(EXTRACTED, sub, "pars.txt")) if l.strip()]
arr = np.loadtxt(os.path.join(EXTRACTED, sub, "chain_1.txt"))
x_all = arr[:, pars.index(par)]
lines.append("C2 gamma, borda de baixo. Artigo -%.2f, ou seja p5 em %.4f" % (tmi, tm - tmi))
lines.append("varredura de burn-in:")
for frac in (0.0, 0.05, 0.10, 0.15, 0.20, 0.25, 0.30, 0.40, 0.50):
    x = x_all[int(len(x_all) * frac):]
    med = np.median(x)
    p5 = np.percentile(x, 5.0)
    lines.append("   burn %4.0f%%  n %5d  mediana %+.4f  p5 %+.4f  menos %.4f  (erro %+.4f)"
                 % (frac * 100, len(x), med, p5, med - p5, (med - p5) - tmi))

# 2. interpolation method, at the frozen 25% burn-in
lines.append("")
lines.append("metodo de interpolacao do percentil, com burn-in de 25%:")
x = x_all[len(x_all) // 4:]
med = np.median(x)
for m in METHODS:
    try:
        p5 = np.percentile(x, 5.0, method=m)
    except Exception as e:
        lines.append("   %-26s erro %s" % (m, e))
        continue
    lines.append("   %-26s menos %.4f  (erro %+.4f)" % (m, med - p5, (med - p5) - tmi))

# 3. the same two knobs, seen across all six numbers, to show the scale of the effect
lines.append("")
lines.append("efeito do burn-in nas seis grandezas (borda de baixo, 0% contra 25%):")
for label, (sub, par, tm2, tp2, tmi2) in CASES.items():
    p = [l.strip() for l in io.open(os.path.join(EXTRACTED, sub, "pars.txt")) if l.strip()]
    a = np.loadtxt(os.path.join(EXTRACTED, sub, "chain_1.txt"))[:, p.index(par)]
    def minus(v):
        return float(np.median(v) - np.percentile(v, 5.0))
    lines.append("   %-12s 0%% %.4f   25%% %.4f   artigo %.2f" % (label, minus(a), minus(a[len(a)//4:]), tmi2))

txt = "\n".join(lines) + "\n"
io.open(os.path.join(ROOT, "runs", "logs", "processing_scan.log"), "w", encoding="utf-8", newline="\n").write(txt)
print(txt)
