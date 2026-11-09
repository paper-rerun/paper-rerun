import sys, json, numpy as np
from la_forge import core
from emcee.autocorr import integrated_time
W = sys.argv[1]; B = W + '/review_scratch/blobs/'; P = W + '/sources/repo/tutorials/presampled_cores/'
fg = np.load(B + 'nano15_hd_chain_fg_long_050523.npy')
print('fg shape', fg.shape, fg.dtype)
x = fg.ravel()
print('fg long chain 5/50/95 A:', 10**np.percentile(x, [5, 50, 95]), 'n', x.size, 'tau', integrated_time(x, quiet=True)[0])
vg = np.load(B + 'nano15_hd_chain_long_050523.npy'); print('vg shape', vg.shape)
print('vg A 5/50/95', 10**np.percentile(vg[:, 1], [5, 50, 95]), 'gamma', np.percentile(vg[:, 0], [5, 50, 95]))
c = core.Core(corepath=P + 'curn_hd.core')
nm = c.get_param('nmodel'); la = c.get_param('gw_hd_log10_A')[nm > 0.5]; lc = c.get_param('gw_crn_log10_A')[nm < 0.5]
from scipy.stats import ks_2samp
print('KS curn_hd HD branch vs fg long:', ks_2samp(la, x))
ml = -14.673301816894826
print('percentile of optstat ML in CURN branch:', 100*np.mean(lc < ml))
# which rows are HD: is the core a contiguous segment of fg long?
print('HD branch first 5', la[:5]); print('fg long has any exact match of first HD value?', np.isin(la[:50], x).sum())
# full chain burn 0 check
c0 = core.Core(corepath=P + 'curn_hd.core', burn=0)
print('curn_hd lnlike etc params tail', c0.params[-8:])
# production product-space core from repo history
p = core.Core(corepath=B + '14f_PL_hd_crn.core')
print('14f_PL_hd_crn params tail', p.params[-8:], 'chain', p.chain.shape, 'burn', p.burn)
nm2 = p.get_param('nmodel')
print('nmodel range', nm2.min(), nm2.max(), 'frac>0.5', np.mean(nm2 > 0.5))
for k in [q for q in p.params if q.startswith('gw')]:
    v = p.get_param(k); print(k, v.min(), np.median(v), v.max())
