#!/bin/bash
source /mnt/e/Ciencia/noturno/2023-abbott-gwtc3-population/env/activate.sh
python - <<'PY'
import cupy, time
print("cupy", cupy.__version__, cupy.cuda.runtime.runtimeGetVersion(), cupy.cuda.runtime.driverGetVersion())
x = cupy.random.uniform(1, 2, 10**6).astype(cupy.float64)
print("sum", float(cupy.exp(x).sum()), float(cupy.log(x).mean()))
from scipy.special import erf
import cupyx.scipy.special as cs
print("erf", float(cs.erf(x).mean()))
print(cupy.cuda.Device(0).compute_capability)
PY
