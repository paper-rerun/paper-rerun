# Summarise a PTMCMC chain's CRS power-law parameters.
# Usage: python -I summarise.py <chaindir_or_chainfile> <parsfile> [burnfrac]
import sys, os, json
import numpy as np

def load(chain_path, pars_path, burnfrac=0.25):
    pars = [l.strip() for l in open(pars_path) if l.strip()]
    data = np.loadtxt(chain_path)
    n = data.shape[0]
    burn = int(n * burnfrac)
    return pars, data[burn:, :len(pars)], n

def hpd(x, cred=0.90):
    xs = np.sort(x)
    n = len(xs)
    k = int(np.floor(cred * n))
    widths = xs[k:] - xs[:n - k]
    i = int(np.argmin(widths))
    return xs[i], xs[i + k]

def summarise(x):
    med = float(np.median(x))
    mean = float(np.mean(x))
    lo, hi = np.percentile(x, [5, 95])
    h = np.histogram(x, bins=100)
    mode = float(0.5 * (h[1][np.argmax(h[0])] + h[1][np.argmax(h[0]) + 1]))
    hl, hh = hpd(x)
    return {
        "n": len(x),
        "median": med, "mean": mean, "mode_hist100": mode,
        "q05": float(lo), "q95": float(hi),
        "median_minus": float(med - lo), "median_plus": float(hi - med),
        "mode_minus": float(mode - lo), "mode_plus": float(hi - mode),
        "hpd90_lo": float(hl), "hpd90_hi": float(hh),
        "mode_hpd_minus": float(mode - hl), "mode_hpd_plus": float(hh - mode),
        "median_hpd_minus": float(med - hl), "median_hpd_plus": float(hh - med),
    }

if __name__ == "__main__":
    chain, parsf = sys.argv[1], sys.argv[2]
    bf = float(sys.argv[3]) if len(sys.argv) > 3 else 0.25
    pars, d, ntot = load(chain, parsf, bf)
    out = {"chain": chain, "pars_file": parsf, "n_total": ntot, "burnfrac": bf, "params": {}}
    for i, p in enumerate(pars):
        pl = p.lower()
        if ("crs" in pl or "gw" in pl or "curn" in pl) and ("log10_a" in pl or "gamma" in pl):
            out["params"][p] = summarise(d[:, i])
    out["all_par_names_tail"] = pars[-12:]
    print(json.dumps(out, indent=1))
