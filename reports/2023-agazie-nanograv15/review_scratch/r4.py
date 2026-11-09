import sys, numpy as np
from la_forge import core
W = sys.argv[1]
c = core.Core(corepath=W + '/sources/repo/tutorials/presampled_cores/curn_hd.core')
nm = c.get_param('nmodel'); la = c.get_param('gw_hd_log10_A')[nm > 0.5]
for nb in (10, 20, 30):
    b = np.array_split(la, nb)
    qs = np.array([10 ** np.percentile(x, [5, 50, 95]) for x in b])
    print('batches', nb, 'SE of p05/p50/p95 (x1e-15):', qs.std(axis=0, ddof=1) / np.sqrt(nb) * 1e15)
