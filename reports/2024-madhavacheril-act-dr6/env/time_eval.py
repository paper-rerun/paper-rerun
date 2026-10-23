# Time one posterior evaluation of a Cobaya yaml at its reference point
# usage: OMP_NUM_THREADS=n python time_eval.py <yaml> [n_evals]
import sys
import time
import numpy as np
from cobaya.model import get_model
from cobaya.yaml import yaml_load_file

info = yaml_load_file(sys.argv[1])
number_of_evals = int(sys.argv[2]) if len(sys.argv) > 2 else 3
info.pop("sampler", None)
model = get_model(info)
# Shift the point a bit each time so CAMB is really recomputed
reference_point = model.prior.reference(random_state=1)
for index in range(number_of_evals):
	point = reference_point * (1.0 + 1e-4 * (index + 1))
	start_time = time.time()
	logpost = model.logposterior(point)
	print(f"eval {index}: {time.time() - start_time:.2f} s  logpost = {logpost.logpost:.3f}  loglikes = {logpost.loglikes}")
