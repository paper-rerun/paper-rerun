import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
from safeload import load_chain

try:
    import psutil
    psutil.Process().nice(psutil.IDLE_PRIORITY_CLASS)
except Exception as e:
    print('nice failed: %r' % (e,))

path = sys.argv[1]
params, arr = load_chain(path)
keys = list(params.keys())
print('n keys', len(keys), 'array shape', arr.shape, arr.dtype)
print('--- non-pulsar keys and their index ---')
for i, k in enumerate(keys):
    if 'red_noise' not in k:
        print(i, repr(k), params[k])
print('--- first 3 keys ---', keys[:3])
print('--- last 8 keys ---', keys[-8:])
print('--- col stats for non-pulsar cols ---')
for i, k in enumerate(keys):
    if 'red_noise' not in k and i < arr.shape[1]:
        c = arr[:, i]
        print('%3d %-28s min %.4f max %.4f mean %.4f sd %.4f' % (i, k, c.min(), c.max(), c.mean(), c.std()))
