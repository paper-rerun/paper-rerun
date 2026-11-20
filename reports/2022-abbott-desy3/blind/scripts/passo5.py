import numpy as np
from analisa import load, col, wq, wcdf, hpdi, get_param, TARGETS

def kde_hpd(x, w, frac=0.68, nbin=2000, smooth=1.0):
    # Smoothed 1D marginal, then the density level whose region holds `frac`
    lo, hi = wq(x, w, [1e-5, 1 - 1e-5])
    pad = 0.1 * (hi - lo)
    edges = np.linspace(lo - pad, hi + pad, nbin + 1)
    cen = 0.5 * (edges[1:] + edges[:-1])
    h, _ = np.histogram(x, bins=edges, weights=w)
    # Gaussian kernel with width = smooth * (Scott rule on the effective sample size)
    neff = w.sum() ** 2 / np.sum(w ** 2)
    sd = np.sqrt(np.sum(w * (x - np.sum(w * x) / w.sum()) ** 2) / w.sum())
    bw = smooth * 1.06 * sd * neff ** (-0.2)
    nk = max(int(4 * bw / (cen[1] - cen[0])), 1)
    t = np.arange(-nk, nk + 1) * (cen[1] - cen[0])
    k = np.exp(-0.5 * (t / bw) ** 2)
    dens = np.convolve(h, k / k.sum(), mode='same')
    # Bisect the density level
    order = np.argsort(dens)[::-1]
    cum = np.cumsum(dens[order]) / dens.sum()
    j = np.searchsorted(cum, frac)
    level = dens[order[min(j, len(order) - 1)]]
    inside = cen[dens >= level]
    return inside.min(), inside.max(), bw

print('alvo'.ljust(34), 'impresso'.ljust(18), 'HPD cru'.ljust(18), 'HPD suave'.ljust(18), 'bw')
for fn, targets in TARGETS.items():
    try:
        d, n = load('dados/' + fn)
    except Exception as e:
        print(fn, 'indisponivel:', e); continue
    w = col(d, 'weight'); w = w / w.sum()
    for name, c, up, dn in targets:
        x = get_param(d, name)
        m = float(np.sum(w * x))
        a, b = hpdi(x, w)
        a2, b2, bw = kde_hpd(x, w)
        print(('%s %s' % (fn.replace('chain_', '').replace('.txt', ''), name)).ljust(34),
              ('%+.3f %+.4f %+.4f' % (c, up, dn)).ljust(18),
              ('%+.4f %+.4f' % (b - m, a - m)).ljust(18),
              ('%+.4f %+.4f' % (b2 - m, a2 - m)).ljust(18),
              '%.4f' % bw)
