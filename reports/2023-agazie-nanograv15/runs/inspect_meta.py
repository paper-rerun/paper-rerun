# Dump the metadata / pars2pull / slicedirs of each core, and the TI column names
import glob, os, sys, json
import h5py, numpy as np
D = sys.argv[1]
def show(name, obj):
    if isinstance(obj, h5py.Dataset):
        v = obj[()]
        s = repr(v)
        print('   ', name, obj.shape, s[:800])
for f in sorted(glob.glob(D + '/*.core')):
    print('=====', os.path.basename(f))
    with h5py.File(f, 'r') as h:
        h['metadata'].visititems(show) if isinstance(h['metadata'], h5py.Group) else show('metadata', h['metadata'])
        for k in ('pars2pull', 'slicedirs'):
            if k in h: show(k, h[k])
        p = [x.decode() if isinstance(x, bytes) else x for x in h['params'][()]]
        print('   params[:5]', p[:5], 'params[-6:]', p[-6:])
ml = json.load(open(sys.argv[2]))
print('optstat_ml_gamma4p33.json gw keys:', {k: v for k, v in ml.items() if 'gw' in k})
