import numpy as np, json
from analisa import load, col, wq, wcdf, hpdi, get_param, TARGETS, summarize
from passo5 import kde_hpd

TOL_C = lambda name, s: max(0.01 if name == 'w' else 0.002, 0.20 * abs(s))
TOL_L = lambda name, s: max(0.01 if name == 'w' else 0.002, 0.15 * abs(s))

rows = []
for fn, targets in TARGETS.items():
    d, n = load('dados/' + fn)
    w = col(d, 'weight'); w = w / w.sum()
    neff = 1.0 / np.sum(w ** 2)
    print('## %s: %d amostras, neff(Kish)=%.0f' % (fn, len(w), neff))
    for name, c, up, dn in targets:
        x = get_param(d, name)
        s = summarize(x, w)
        a2, b2, bw = kde_hpd(x, w)
        s['D3s'] = (a2 - s['mean'], b2 - s['mean'])
        r = {'cadeia': fn, 'par': name, 'imp_c': c, 'imp_up': up, 'imp_dn': dn,
             'media': s['mean'], 'mediana': s['median'], 'F_media': s['F(mean)'], 'bw': bw}
        for k in ['D1', 'D2', 'D3', 'D3s', 'D4', 'D5']:
            r[k] = [s[k][1], s[k][0]]
            r['ok_' + k] = bool(abs(s[k][1] - up) <= TOL_L(name, up) and abs(s[k][0] - dn) <= TOL_L(name, dn))
        r['ok_central'] = bool(abs(s['mean'] - c) <= TOL_C(name, up))
        rows.append(r)
json.dump(rows, open('resultados.json', 'w'), indent=1)

hdr = '| cadeia | par | impresso | media | D1 (pre-reg) | D2 16/84 | D3 HPD cru | D3s HPD suave | D4 simetrico | D5 mediana |'
print(hdr); print('|' + '---|' * 10)
for r in rows:
    cells = []
    for k in ['D1', 'D2', 'D3', 'D3s', 'D4', 'D5']:
        cells.append('%+.4f %+.4f %s' % (r[k][0], r[k][1], 'OK' if r['ok_' + k] else 'X'))
    print('| %s | %s | %.3f %+.3f %+.3f | %.4f %s | %s |' % (
        r['cadeia'].replace('chain_', '').replace('.txt', ''), r['par'],
        r['imp_c'], r['imp_up'], r['imp_dn'], r['media'], 'OK' if r['ok_central'] else 'X',
        ' | '.join(cells)))
print()
for k in ['D1', 'D2', 'D3', 'D3s', 'D4', 'D5']:
    print('%s: %d/%d limites OK' % (k, sum(r['ok_' + k] for r in rows), len(rows)))
print('centrais: %d/%d OK' % (sum(r['ok_central'] for r in rows), len(rows)))
