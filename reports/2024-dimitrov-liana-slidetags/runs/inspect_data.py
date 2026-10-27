# D01 check: X log-normalised (expm1 row sums ~1e4), layers['raw'] integer counts, obsm['spatial'], the 9 method keys in .uns
import numpy as np, scanpy as sc
from common import d, DATA
import os
for k, v in d.items():
    a = sc.read_h5ad(os.path.join(DATA, f'{k}.h5ad'))
    rs = np.asarray(np.expm1(a.X[:200].toarray() if hasattr(a.X, 'toarray') else a.X[:200]).sum(1)).ravel()
    raw = a.layers['raw']; rawv = raw.data if hasattr(raw, 'data') else np.asarray(raw)
    print(k, v, 'shape', a.shape, 'X dtype', a.X.dtype, 'expm1 rowsum[0:200] min/max %.1f/%.1f' % (rs.min(), rs.max()),
          'raw integer', bool(np.all(np.mod(rawv[:100000], 1) == 0)), 'spatial', a.obsm['spatial'].shape,
          'n cell types', a.obs['cell_type'].nunique())
    print('   uns keys', sorted(a.uns.keys()))
    for m in sorted(a.uns.keys()):
        if hasattr(a.uns[m], 'shape'):
            print('   ', m, a.uns[m].shape, list(a.uns[m].columns))
