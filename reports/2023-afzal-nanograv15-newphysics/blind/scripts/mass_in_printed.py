"""Diagnostic: what fraction of the posterior samples actually falls inside the
interval the paper printed? If it is 0.68 the printed interval is a legitimate HPD of
a slightly different shape; if it is far from 0.68 the printed interval and my
posterior disagree about more than smoothing.

usage: mass_in_printed.py <model> <NP|NPSMBHB> <chains_dir> <out_json>
"""
import ctypes, json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
from safeload import load_chain
from compute_one import FILESTEM, COLNAME, COLNAME_BY_MODEL, PRIORS

try:
    ctypes.windll.kernel32.SetPriorityClass(ctypes.windll.kernel32.GetCurrentProcess(), 0x00000040)
except Exception:
    pass

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
printed = json.load(open(os.path.join(HERE, 'out', 'table4_printed.json')))

model, analysis, chains_dir, out_json = sys.argv[1:5]
fname = FILESTEM[model] + ('_bhb' if analysis == 'NPSMBHB' else '') + '.pkl.gz'
params, arr = load_chain(os.path.join(chains_dir, fname))
idx = {k: i for i, k in enumerate(params.keys())}
ckey = 'ci68_NP' if analysis == 'NP' else 'ci68_NPSMBHB'

res = {}
for prow in printed:
    if prow['model'] != model or prow[ckey] is None:
        continue
    p = prow['param']
    col = COLNAME_BY_MODEL.get((model, p), COLNAME.get(p, p))
    if col not in idx:
        continue
    x = arr[:, idx[col]]
    lo, hi = prow[ckey]['lo'], prow[ckey]['hi']
    inside = float(np.count_nonzero((x >= lo) & (x <= hi))) / x.size
    res[p] = {'printed': [lo, hi], 'mass_inside_printed': inside,
              'width_printed': hi - lo}
json.dump({'model': model, 'analysis': analysis, 'params': res}, open(out_json, 'w'), indent=1)
print('ok', model, analysis, {k: round(v['mass_inside_printed'], 4) for k, v in res.items()})
