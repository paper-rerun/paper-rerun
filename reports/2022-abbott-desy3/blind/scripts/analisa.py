import sys, numpy as np

def load(path):
    # Header is the first line, TAB separated, prefixed by '#'
    with open(path) as f:
        head = f.readline()
    names = head.lstrip('#').rstrip('\n').split('\t')
    names = [n.strip() for n in names]
    data = np.loadtxt(path, comments='#')
    assert data.shape[1] == len(names), (data.shape, len(names))
    return {n.lower(): data[:, i] for i, n in enumerate(names)}, data.shape[0]

def col(d, key):
    # Match by header name only, never by fixed index
    cands = [k for k in d if k.endswith(key.lower())]
    assert len(cands) == 1, (key, cands)
    return d[cands[0]]

def wq(x, w, p):
    # Weighted quantile, linear interpolation on the mid-point CDF
    i = np.argsort(x)
    x, w = x[i], w[i]
    c = np.cumsum(w)
    c = (c - 0.5 * w) / c[-1]
    return np.interp(p, c, x)

def wcdf(x, w, v):
    i = np.argsort(x)
    x, w = x[i], w[i]
    c = np.cumsum(w)
    c = (c - 0.5 * w) / c[-1]
    return np.interp(v, x, c)

def hpdi(x, w, frac=0.68, ngrid=4096):
    # Smallest interval holding `frac` of the volume, from the weighted CDF on a grid
    lo, hi = wq(x, w, [1e-5, 1 - 1e-5])
    g = np.linspace(lo, hi, ngrid)
    c = wcdf(x, w, g)
    best = None
    for j in range(ngrid):
        tgt = c[j] + frac
        if tgt > c[-1]:
            break
        k = np.searchsorted(c, tgt)
        if k >= ngrid:
            break
        width = g[k] - g[j]
        if best is None or width < best[0]:
            best = (width, g[j], g[k])
    return best[1], best[2]

def sym_about(x, w, m, frac=0.68):
    # Smallest d with P(m-d < x < m+d) = frac
    lo, hi = wq(x, w, [1e-6, 1 - 1e-6])
    dmax = max(hi - m, m - lo)
    d = np.linspace(0, dmax, 20001)
    mass = wcdf(x, w, m + d) - wcdf(x, w, m - d)
    return float(np.interp(frac, mass, d))

def summarize(x, w):
    w = w / w.sum()
    mean = float(np.sum(w * x))
    med = float(wq(x, w, 0.5))
    p0 = float(wcdf(x, w, mean))
    out = {'mean': mean, 'median': med, 'F(mean)': p0}
    # D1: 34% of volume on each side of the mean
    lo1 = float(wq(x, w, max(p0 - 0.34, 0.0)))
    hi1 = float(wq(x, w, min(p0 + 0.34, 1.0)))
    out['D1'] = (lo1 - mean, hi1 - mean)
    # D2: equal-tail 16/84 about the mean
    q16, q84 = [float(v) for v in wq(x, w, [0.16, 0.84])]
    out['D2'] = (q16 - mean, q84 - mean)
    # D3: HPDI 68% about the mean
    a, b = hpdi(x, w)
    out['D3'] = (a - mean, b - mean)
    # D4: symmetric in x about the mean
    d = sym_about(x, w, mean)
    out['D4'] = (-d, d)
    # D5: equal-tail about the median
    out['D5'] = (q16 - med, q84 - med)
    return out

TARGETS = {
 'chain_3x2pt_lcdm_SR_maglim.txt': [('S_8',0.776,0.017,-0.017), ('Omega_m',0.339,0.032,-0.031), ('sigma_8',0.733,0.039,-0.049)],
 'chain_3x2pt_wcdm_SR_maglim.txt': [('S_8',0.775,0.026,-0.024), ('Omega_m',0.352,0.035,-0.041), ('sigma_8',0.719,0.037,-0.044), ('w',-0.98,0.32,-0.20)],
 'chain_all_lcdm.txt': [('S_8',0.812,0.008,-0.008), ('Omega_m',0.306,0.004,-0.005), ('h',0.680,0.004,-0.003)],
}

def get_param(d, name):
    if name == 'Omega_m':
        return col(d, '--omega_m')
    if name == 'sigma_8':
        return col(d, '--sigma_8')
    if name == 'h':
        return col(d, '--h0')
    if name == 'w':
        return col(d, '--w')
    if name == 'S_8':
        return col(d, '--sigma_8') * np.sqrt(col(d, '--omega_m') / 0.3)
    raise KeyError(name)

if __name__ == '__main__':
  for fn, targets in TARGETS.items():
      d, n = load('dados/' + fn)
      w = col(d, 'weight')
      print('=== %s  (%d amostras, soma de peso %.6g, peso max/soma %.3g)' % (fn, n, w.sum(), w.max()/w.sum()))
      print('    neff (Kish) = %.1f' % (w.sum()**2 / np.sum(w**2)))
      for name, c, up, dn in targets:
          x = get_param(d, name)
          s = summarize(x, w)
          print('  %-8s impresso: %+.4f %+.4f %+.4f' % (name, c, up, dn))
          print('           media=%.5f  mediana=%.5f  F(media)=%.4f' % (s['mean'], s['median'], s['F(mean)']))
          for k in ['D1','D2','D3','D4','D5']:
              print('           %s: %+.4f %+.4f' % (k, s[k][1], s[k][0]))
      print()
  