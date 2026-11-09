# List parameters, shapes, burn and stored metadata of every presampled core
import glob, os, sys, inspect
import numpy as np, h5py
import la_forge, la_forge.core as co
print('la_forge', la_forge.__version__)
print('Core signature:', inspect.signature(co.Core.__init__))
D = sys.argv[1]
for f in sorted(glob.glob(D + '/*.core')):
    print('\n=====', os.path.basename(f))
    with h5py.File(f, 'r') as h:
        for k in h.keys():
            obj = h[k]
            print('  h5 key', k, getattr(obj, 'shape', ''), getattr(obj, 'dtype', ''))
        print('  attrs', dict(h.attrs))
    if '_ti' in f:
        continue
    c = co.Core(corepath=f)
    print('  chain shape', c.chain.shape, 'burn', c.burn, 'nparams', len(c.params))
    gw = [p for p in c.params if 'gw' in p or p in ('nmodel', 'lnpost', 'lnlike')]
    print('  gw/meta params', gw[:12], '...' if len(gw) > 12 else '', len(gw))
    for p in gw:
        if 'gamma' in p or 'log10_A' in p or p == 'nmodel':
            x = c.get_param(p)
            print(f'   {p}: n={x.size} min={x.min():.6g} max={x.max():.6g} median={np.median(x):.6g}')
    for attr in ('runtime_info', 'jumps', 'jump_fractions', 'hot_chains', 'priors'):
        v = getattr(c, attr, None)
        if v is not None and len(v):
            s = str(v)
            print(f'  {attr}:', s[:1500])
