#!/bin/bash
# CPU only: dump inputs/scores from each weaver version, compare inputs, then cross-feed
H=/mnt/e/Ciencia/noturno/2022-qu-particle-transformer
O=$H/runs/diag_weaver053
export CUDA_VISIBLE_DEVICES=""
export MPLBACKEND=Agg
cd $O
$H/env/.venv/bin/python $H/runs/diag_weaver053.py dump w0417 $O 2>&1 | grep -E "^w0|Error|Traceback|line"
$H/env/.venv-0.5.3/bin/python $H/runs/diag_weaver053.py dump w053 $O 2>&1 | grep -E "^w0|Error|Traceback|line"
$H/env/.venv/bin/python - <<PY
import numpy as np
a=np.load('$O/diag_w0417.npz'); b=np.load('$O/diag_w053.npz')
print('jet_pt equal', np.array_equal(a['jet_pt'], b['jet_pt']))
for k in a.files:
    if k in ('jet_pt','scores'): continue
    if k not in b.files: print(k,'missing in 0.5.3'); continue
    x,y=a[k],b[k]
    if x.shape!=y.shape: print(k,'shape',x.shape,y.shape); continue
    d=np.abs(x-y)
    print(k, x.shape, 'max |diff| %.3g' % d.max(), 'n entries differing', int((d>1e-6).sum()))
PY
$H/env/.venv/bin/python $H/runs/diag_weaver053.py feed w0417 $O/diag_w053.npz $O 2>&1 | grep -E "^w0|Error|Traceback"
$H/env/.venv-0.5.3/bin/python $H/runs/diag_weaver053.py feed w053 $O/diag_w0417.npz $O 2>&1 | grep -E "^w0|Error|Traceback"
