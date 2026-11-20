import numpy as np
from analisa import load, col, get_param, TARGETS
from passo5 import kde_hpd
TOL = lambda name, s: max(0.01 if name == 'w' else 0.002, 0.15 * abs(s))
sm = [0.5, 0.75, 1.0, 1.5, 2.0, 3.0]
print('suavizacao (fator sobre a regra de Scott) x limites OK de 10, e pior desvio')
res = {s: [0, 0.0] for s in sm}
det = {s: [] for s in sm}
for fn, targets in TARGETS.items():
    d, n = load('dados/' + fn)
    w = col(d, 'weight'); w = w / w.sum()
    for name, c, up, dn in targets:
        x = get_param(d, name); m = float(np.sum(w * x))
        for s in sm:
            a, b, bw = kde_hpd(x, w, smooth=s)
            du, dd = (b - m) - up, (a - m) - dn
            ok = abs(du) <= TOL(name, up) and abs(dd) <= TOL(name, dn)
            res[s][0] += ok
            res[s][1] = max(res[s][1], abs(du) / TOL(name, up), abs(dd) / TOL(name, dn))
            if not ok:
                det[s].append('%s/%s' % (fn.replace('chain_', '')[:12], name))
for s in sm:
    print('  smooth=%.2f  %d/10 OK  pior desvio = %.2f da tolerancia  %s' % (s, res[s][0], res[s][1], ','.join(det[s])))
