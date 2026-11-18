"""Diagnostic, not part of the frozen rule: is the paper's 90% region equal-tailed or HPD?

The frozen route takes the 5th and 95th percentiles. If the authors used the highest
posterior density interval instead, an asymmetric marginal would show the difference, and
gamma in DR2new is the most asymmetric of the six we check.
"""
import io, json, os
import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EXTRACTED = os.path.join(ROOT, "data", "extracted")

CASES = {
    "C1": ("DR2full__hd_pl/hd_pl", "gw_hd"),
    "C2": ("DR2new__hd_pl/hd_pl", "gw_hd"),
    "C3": ("DR2full__crn_pl/crn_pl", "gw_crn"),
}
PAPER = {
    "C1": {"log10_A": (-14.54, 0.28, 0.41), "gamma": (4.19, 0.73, 0.63)},
    "C2": {"log10_A": (-13.94, 0.23, 0.48), "gamma": (2.71, 1.18, 0.71)},
    "C3": {"log10_A": (-14.53, 0.29, 0.44), "gamma": (4.13, 0.80, 0.59)},
}


def hpd(x, mass=0.90):
    """Narrowest interval holding `mass` of the samples."""
    s = np.sort(x)
    n = len(s)
    k = int(np.floor(mass * n))
    widths = s[k:] - s[: n - k]
    i = int(np.argmin(widths))
    return float(s[i]), float(s[i + k])


out = {}
lines = ["comparacao das duas definicoes de intervalo de 90%, contra o artigo", ""]
for cid, (sub, prefix) in CASES.items():
    pars = [l.strip() for l in io.open(os.path.join(EXTRACTED, sub, "pars.txt")) if l.strip()]
    arr = np.loadtxt(os.path.join(EXTRACTED, sub, "chain_1.txt"))
    burn = arr.shape[0] // 4
    out[cid] = {}
    for short in ("log10_A", "gamma"):
        col = pars.index(prefix + "_" + short)
        x = arr[burn:, col]
        med = float(np.median(x))
        p5, p95 = (float(v) for v in np.percentile(x, [5.0, 95.0]))
        h_lo, h_hi = hpd(x)
        tm, tp, tmi = PAPER[cid][short]
        rec = {
            "median": med,
            "equal_tailed": {"plus": p95 - med, "minus": med - p5},
            "hpd": {"plus": h_hi - med, "minus": med - h_lo},
            "paper": {"plus": tp, "minus": tmi},
            "err_equal_tailed": {"plus": (p95 - med) - tp, "minus": (med - p5) - tmi},
            "err_hpd": {"plus": (h_hi - med) - tp, "minus": (med - h_lo) - tmi},
        }
        out[cid][short] = rec
        lines.append("%s %-8s artigo +%.2f -%.2f" % (cid, short, tp, tmi))
        lines.append("            percentil  +%.4f -%.4f   (erro %+.4f %+.4f)"
                     % (rec["equal_tailed"]["plus"], rec["equal_tailed"]["minus"],
                        rec["err_equal_tailed"]["plus"], rec["err_equal_tailed"]["minus"]))
        lines.append("            HPD        +%.4f -%.4f   (erro %+.4f %+.4f)"
                     % (rec["hpd"]["plus"], rec["hpd"]["minus"],
                        rec["err_hpd"]["plus"], rec["err_hpd"]["minus"]))

eq = sum(abs(v[s]["err_equal_tailed"][b]) for v in out.values() for s in v for b in ("plus", "minus"))
hp = sum(abs(v[s]["err_hpd"][b]) for v in out.values() for s in v for b in ("plus", "minus"))
lines += ["", "soma do erro absoluto nas 12 bordas: percentil %.4f, HPD %.4f" % (eq, hp)]
txt = "\n".join(lines) + "\n"
io.open(os.path.join(ROOT, "runs", "logs", "interval_shape.log"), "w", encoding="utf-8", newline="\n").write(txt)
io.open(os.path.join(ROOT, "runs", "out", "interval_shape.json"), "w", encoding="utf-8", newline="\n").write(json.dumps(out, indent=1) + "\n")
print(txt)
