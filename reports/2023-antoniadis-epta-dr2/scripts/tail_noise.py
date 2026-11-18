"""Diagnostic: how well is the 5th percentile of gamma determined by a 30k MCMC chain?

The one number that misses the frozen band is the lower bound of gamma in DR2new, by
0.0022. Before calling that a disagreement with the paper, measure how much that quantile
moves under resampling. MCMC samples are correlated, so a naive bootstrap understates the
spread; a moving-block bootstrap with a block longer than the autocorrelation length does not.
"""
import io, json, os
import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EXTRACTED = os.path.join(ROOT, "data", "extracted")
RNG = np.random.default_rng(20261118)
N_BOOT = 2000


def act(x):
    """Integrated autocorrelation time, Sokal windowing."""
    x = x - x.mean()
    n = len(x)
    f = np.fft.rfft(x, 2 * n)
    acf = np.fft.irfft(f * np.conjugate(f))[:n].real
    acf /= acf[0]
    tau = 1.0
    for m in range(1, n):
        tau_m = 1.0 + 2.0 * acf[1:m + 1].sum()
        if m >= 5 * tau_m:
            return float(tau_m)
        tau = tau_m
    return float(tau)


def block_bootstrap_quantile(x, q, block, n_boot=N_BOOT):
    n = len(x)
    n_blocks = int(np.ceil(n / block))
    starts = RNG.integers(0, n - block, size=(n_boot, n_blocks))
    out = np.empty(n_boot)
    idx = np.arange(block)
    for i in range(n_boot):
        s = (starts[i][:, None] + idx[None, :]).ravel()[:n]
        out[i] = np.percentile(x[s], q)
    return out


CASES = {
    "C1": ("DR2full__hd_pl/hd_pl", "gw_hd"),
    "C2": ("DR2new__hd_pl/hd_pl", "gw_hd"),
    "C3": ("DR2full__crn_pl/crn_pl", "gw_crn"),
}

res, lines = {}, []
for cid, (sub, prefix) in CASES.items():
    pars = [l.strip() for l in io.open(os.path.join(EXTRACTED, sub, "pars.txt")) if l.strip()]
    arr = np.loadtxt(os.path.join(EXTRACTED, sub, "chain_1.txt"))
    burn = arr.shape[0] // 4
    res[cid] = {}
    for short in ("log10_A", "gamma"):
        x = arr[burn:, pars.index(prefix + "_" + short)]
        tau = act(x)
        block = max(1, int(np.ceil(5 * tau)))
        ess = len(x) / tau
        d = {"act": tau, "ess": ess, "block": block, "n": int(len(x))}
        for q, tag in ((5.0, "p5"), (50.0, "median"), (95.0, "p95")):
            b = block_bootstrap_quantile(x, q, block)
            d[tag] = {"value": float(np.percentile(x, q)), "boot_sd": float(b.std(ddof=1))}
        res[cid][short] = d
        lines.append("%s %-8s tau %.1f  ESS %.0f  bloco %d" % (cid, short, tau, ess, block))
        lines.append("            sd do bootstrap em bloco:  p5 %.4f   mediana %.4f   p95 %.4f"
                     % (d["p5"]["boot_sd"], d["median"]["boot_sd"], d["p95"]["boot_sd"]))

txt = "\n".join(lines) + "\n"
io.open(os.path.join(ROOT, "runs", "logs", "tail_noise.log"), "w", encoding="utf-8", newline="\n").write(txt)
io.open(os.path.join(ROOT, "runs", "out", "tail_noise.json"), "w", encoding="utf-8", newline="\n").write(json.dumps(res, indent=1) + "\n")
print(txt)
