import sys, numpy as np
from la_forge import core
from emcee.autocorr import integrated_time
W = sys.argv[1]; R = W + '/sources/repo/'
pb = np.load(R + 'data_release/figure_3/pshift_bfs.npy')
s = np.sort(pb)[::-1]
print('n', pb.size, 'finite', np.isfinite(pb).sum(), 'n nan', np.isnan(pb).sum(), 'top 8', s[:8])
print('>226', (pb > 226).sum(), '>=200', (pb >= 200).sum(), '>150', (pb > 150).sum(), 'unique', np.unique(pb).size)
# product-space BF error with autocorrelation: batch means on nmodel
c = core.Core(corepath=R + 'tutorials/presampled_cores/curn_hd.core')
nm = c.get_param('nmodel'); hd = (nm > 0.5).astype(float)
tau = integrated_time(hd, quiet=True)[0]
p = hd.mean(); n = hd.size
neff = n / tau
sp = np.sqrt(p * (1 - p) / neff)
bf = lambda p: p / (1 - p) * 300
print('tau(indicator)', tau, 'neff', neff, 'BF', bf(p), 'BF 1sig from neff', bf(p + sp) - bf(p), bf(p) - bf(p - sp))
for nb in (10, 20, 50):
    b = np.array_split(hd, nb); ps = np.array([x.mean() for x in b]); bfs = ps / (1 - ps) * 300
    print('batch', nb, 'BF sd of mean', bfs.std(ddof=1) / np.sqrt(nb))
# model switches count
print('switches', np.sum(np.diff(hd) != 0))
