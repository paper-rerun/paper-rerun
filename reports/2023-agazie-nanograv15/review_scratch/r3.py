import sys, numpy as np
pb = np.load(sys.argv[1] + '/sources/repo/data_release/figure_3/pshift_bfs.npy')
u, c = np.unique(pb, return_counts=True)
d = u[c > 1]
print('values repeated', d.size, 'extra copies', (c[c > 1] - 1).sum(), 'max count', c.max())
print('most repeated', sorted(zip(c[c > 1], d), reverse=True)[:6])
print('dtype', pb.dtype, 'min', pb.min())
# are repeats contiguous blocks?
idx = np.where(np.isin(pb, d))[0]; print('first repeat idx', idx[:20])
