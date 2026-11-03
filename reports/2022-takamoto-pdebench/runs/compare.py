# Compare our values with claims.json using its pre-registered rule: match iff '{:.1e}' of ours == paper_value
import json, pickle, os, glob, numpy as np
W = '/mnt/e/Ciencia/noturno/2022-takamoto-pdebench'
d = json.load(open(W + '/claims.json'))
diag = {}
for f in glob.glob(W + '/runs/diag_*.json'):
    diag.update(json.load(open(f)))
# pickle order: RMSE, nRMSE, cRMSE, max, bRMSE, fRMSE[low, mid, high]
def load_pickle(tag):
    p = glob.glob(W + '/runs/jobs/' + tag + '/*.pickle')
    if not p:
        return None
    e = pickle.load(open(p[0], 'rb'))
    return {'RMSE': float(e[0]), 'nRMSE': float(e[1]), 'cRMSE': float(e[2]), 'MAX': float(e[3]), 'bRMSE': float(e[4]),
            'fRMSE_low': float(e[5][0]), 'fRMSE_mid': float(e[5][1]), 'fRMSE_high': float(e[5][2])}
def judge(c, ours):
    pv = float(c['paper_value'])
    if ours is None:
        return dict(id=c['id'], paper=c['paper_value'], ours=None, match=None)
    rel = (ours - pv) / pv
    lo, hi = c['tolerance']['accept_interval_approx']
    edge = min(abs(ours - lo), abs(ours - hi)) / pv < 0.01
    return dict(id=c['id'], paper=c['paper_value'], ours=ours, ours_2sf='{:.1e}'.format(ours),
                match='{:.1e}'.format(ours) == c['paper_value'], rel_diff=rel, near=abs(rel) <= 0.10, within_1pct_of_rounding_edge=edge)
rows, sec = [], []
for c in d['claims']:
    tag = c['id'].replace('-nRMSE', '')
    pk = load_pickle(tag)
    r = judge(c, pk['nRMSE'] if pk else None)
    dg = diag.get(tag)
    if dg:
        r['diag_P_nRMSE'] = dg['P']['nRMSE']; r['V1_nRMSE'] = dg['V1']['nRMSE']
        r['V2_all_slots'] = dg['V2_all_slots']; r['V2_pred_slots'] = dg['V2_pred_slots']
        r['diag_equals_pickle'] = pk is not None and abs(dg['P']['nRMSE'] - pk['nRMSE']) <= 1e-6 * abs(pk['nRMSE'])
    rows.append(r)
for c in d['secondary_claims']:
    m = c['id'].split('-')[-1]
    tag = c['id'][:-(len(m) + 1)]
    pk = load_pickle(tag)
    r = judge(c, pk[m] if pk else None); r['metric'] = m
    dg = diag.get(tag)
    if dg:
        r['V1'] = dg['V1'][{'MAX': 'max'}.get(m, m)]
    sec.append(r)
# Sparse check (D14): beta4.0 on full vs sparse copy
sp = {}
for mdl in ('UNet', 'FNO'):
    a, b = load_pickle('Advection-beta4.0-' + mdl), load_pickle('Advection-beta4.0-' + mdl + '-sparse')
    if a and b:
        sp[mdl] = {'identical_all_8_metrics': all(a[k] == b[k] for k in a), 'full': a, 'sparse': b}
n = sum(1 for r in rows if r['match']); miss = sum(1 for r in rows if r['match'] is False)
verdict = ('Reproduced' if n == 26 else 'Partially reproduced' if n >= 1 and miss >= 1 else 'Not reproduced' if miss == 26 else 'incomplete')
out = dict(primary=rows, secondary=sec, sparse_check=sp, n_match=n, n_miss=miss, verdict_D15=verdict,
           secondary_n_match=sum(1 for r in sec if r['match']), secondary_n=len(sec))
json.dump(out, open(W + '/runs/results.json', 'w'), indent=1)
for r in rows:
    print('%-28s paper %-8s ours %-12s %-8s match=%s rel=%+.3f V1=%s V2=%s' % (r['id'], r['paper'], r.get('ours'), r.get('ours_2sf'), r.get('match'), r.get('rel_diff', float('nan')), r.get('V1_nRMSE'), r.get('V2_all_slots')))
print('primary matches', n, 'misses', miss, '->', verdict)
print('secondary matches', out['secondary_n_match'], '/', len(sec))
print('sparse check', {k: v['identical_all_8_metrics'] for k, v in sp.items()})
