# C1 from the headline chain recovered from the repo's git history (method frozen in claims.json)
import sys, hashlib, json
import numpy as np
from emcee.autocorr import integrated_time
W = sys.argv[1]
B = W + '/review_scratch/blobs/'
print('claims.json sha256', hashlib.sha256(open(W + '/claims.json', 'rb').read()).hexdigest())
def gitblob(path):
    d = open(path, 'rb').read()
    return hashlib.sha1(b'blob %d\0' % len(d) + d).hexdigest(), len(d)
for name in ('nano15_hd_chain_fg_long_050523.npy', 'nano15_hd_chain_long_050523.npy', '14f_PL_hd_crn.core', 'optstat_ml_gamma4p33_fig1.json'):
    print('git blob id', name, *gitblob(B + name))
fg = np.load(B + 'nano15_hd_chain_fg_long_050523.npy')
print('fg shape', fg.shape, 'dtype', fg.dtype, 'log10A min/max', fg.min(), fg.max())
A = 10 ** fg.ravel()
p05, p50, p95 = np.percentile(A, [5, 50, 95])
tau = integrated_time(fg.ravel(), quiet=True)[0]
band = {'median': [2.3e-15, 2.5e-15], 'p05': [1.7e-15, 1.9e-15], 'p95': [3.0e-15, 3.2e-15]}
r = dict(p05=p05, median=p50, p95=p95, plus=p95 - p50, minus=p50 - p05, n=int(A.size), tau_int=float(tau), neff=float(A.size / tau))
r['inside'] = {k: bool(band[k][0] <= r[k] <= band[k][1]) for k in band}
# Batch-means standard error of the three quantiles
for nb in (10, 20, 50):
    qs = np.array([np.percentile(x, [5, 50, 95]) for x in np.array_split(A, nb)])
    print('batch-means SE p05/p50/p95 (x1e-15), nb=%d:' % nb, qs.std(axis=0, ddof=1) / np.sqrt(nb) * 1e15)
print('C1 (history blob):', json.dumps(r, indent=1))
vg = np.load(B + 'nano15_hd_chain_long_050523.npy')
print('vg long shape', vg.shape, 'A 5/50/95', 10 ** np.percentile(vg[:, 1], [5, 50, 95]), 'gamma 5/50/95', np.percentile(vg[:, 0], [5, 50, 95]))
json.dump(r, open(W + '/runs/c1_history_blob.json', 'w'), indent=1)
