#!/bin/bash
O=/mnt/e/Ciencia/noturno/2022-qu-particle-transformer/runs/diag_weaver053
/mnt/e/Ciencia/noturno/2022-qu-particle-transformer/env/.venv/bin/python - <<PY
import numpy as np
a=np.load('$O/diag_w0417.npz'); b=np.load('$O/diag_w053.npz')
m=a['pf_mask'].astype(bool)
for k in ('pf_points','pf_features','pf_vectors'):
    d=np.abs(a[k]-b[k]).max(axis=1,keepdims=True)
    print(k,'max |diff| on real particles %.3g' % d[m].max(), 'on padded slots %.3g' % d[~m].max())
f=np.load('$O/diag_feed_w0417_on_diag_w053.npz.npy')
print('0.4.17 model, 0.5.3 inputs vs 0.4.17 inputs: max |score diff| %.3g' % np.abs(f-a['scores']).max())
g=np.load('$O/diag_feed_w053_on_diag_w0417.npz.npy')
print('0.5.3 model, 0.4.17 inputs vs 0.5.3 inputs: max |score diff| %.3g' % np.abs(g-b['scores']).max())
print('0.5.3 model argmax counts', np.bincount(b['scores'].argmax(1), minlength=10))
PY
