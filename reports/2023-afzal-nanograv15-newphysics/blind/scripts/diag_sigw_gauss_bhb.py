"""Post-hoc diagnostic (NOT part of the pre-registered method).

sigw_gauss_bhb.pkl.gz holds samples whose log_posterior is ~1e12 instead of ~8e6, and
whose gamma_bhb reaches 13.5 although its prior is normal(4.7, 0.346). Find how many
there are and what the Table 4 estimators become once they are dropped.
"""
import ctypes, json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
from safeload import load_chain
from compute_one import shortest_interval, smoothed_density, levelset_interval

try:
    ctypes.windll.kernel32.SetPriorityClass(ctypes.windll.kernel32.GetCurrentProcess(), 0x40)
except Exception:
    pass

path = (r'E:\Ciencia\noturno\2023-afzal-nanograv15-newphysics\extraido\chains'
        r'\stochastic\sigw_gauss_bhb.pkl.gz')
params, arr = load_chain(path)
idx = {k: i for i, k in enumerate(params.keys())}
n = arr.shape[0]
lp = np.array(arr[:, idx['log_posterior']], dtype=float)

print('n samples          ', n)
print('log_posterior range', lp.min(), lp.max())
for thr in (1e7, 1e8, 8.1e6):
    print('  samples with log_posterior > %.3g : %d (%.4f%%)' % (thr, int((lp > thr).sum()), 100.0 * (lp > thr).mean()))

bad = lp > 1e7
first_bad = int(np.argmax(bad)) if bad.any() else -1
print('first bad index', first_bad, 'of', n, '-> fraction', first_bad / n)
# are the bad samples contiguous?
if bad.any():
    where = np.flatnonzero(bad)
    print('bad index min/max', where.min(), where.max(), 'count', where.size,
          'contiguous' if where.size == where.max() - where.min() + 1 else 'scattered')

good = ~bad
RANGES = {'gw_bhb_np_0': None, 'gw_bhb_np_1': None, 'log10_A': (-3, 1),
          'log10_fpeak': (-11, -5), 'width': (0.1, 3)}
PRINTED = {'gw_bhb_np_0': (-15.72, 0.46), 'gw_bhb_np_1': (4.65, 0.34),
           'log10_A': (-0.36, 0.61), 'log10_fpeak': (-6.30, 0.73),
           'width': (1.30, 0.70)}
PRINTED_CI = {'gw_bhb_np_0': (-16.14, -15.22), 'gw_bhb_np_1': (4.32, 5.00),
              'log10_A': (-1.04, 0.24), 'log10_fpeak': (-7.17, -5.57),
              'width': (0.37, 1.92)}
out = {}
for col in RANGES:
    x = np.array(arr[:, idx[col]], dtype=float)
    xg = x[good]
    rng = RANGES[col]
    lo, hi = rng if rng else (float(xg.min()), float(xg.max()))
    c, d = smoothed_density(xg, lo, hi, xg.std() * xg.size ** -0.2)
    ls = levelset_interval(c, d)
    out[col] = {
        'printed_mean_sd': PRINTED[col], 'printed_ci68': PRINTED_CI[col],
        'all_mean': float(x.mean()), 'all_sd': float(x.std()),
        'clean_mean': float(xg.mean()), 'clean_sd': float(xg.std()),
        'clean_n': int(xg.size),
        'clean_hpd68_shortest': list(shortest_interval(np.sort(xg))),
        'clean_hpd68_levelset': list(ls),
        'clean_maxpost': float(c[int(np.argmax(d))]),
    }
    print('%-14s printed %7.2f +- %.2f | all %7.4f +- %.4f | clean %7.4f +- %.4f | '
          'clean ls68 [%.3f, %.3f] printed ci68 [%.2f, %.2f]'
          % (col, PRINTED[col][0], PRINTED[col][1], x.mean(), x.std(),
             xg.mean(), xg.std(), ls[0], ls[1], PRINTED_CI[col][0], PRINTED_CI[col][1]))

json.dump({'n': n, 'n_bad': int(bad.sum()), 'params': out},
          open(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                            'out', 'diag_sigw_gauss_bhb.json'), 'w'), indent=1)
