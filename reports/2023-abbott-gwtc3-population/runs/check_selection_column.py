# Hypothesis: compute_rate_posterior calls selection.detection_efficiency(dict(posterior row)) without
# convert_to_beta_parameters, so alpha_chi/beta_chi (spin-magnitude Beta shape) are whatever the VT model
# held last, the same pair for every row. Test: find one (alpha_chi, beta_chi) that reproduces the published
# 'selection' column for many rows to machine precision.
import json
import sys
import numpy as np
import pandas as pd
from scipy.optimize import minimize
from gwpopulation_pipe import data_analysis, vt_helper
from gwpopulation.conversions import convert_to_beta_parameters

argv = sys.argv[1:]
args, _ = data_analysis.create_parser().parse_known_args(argv)
vt_helper.N_EVENTS = 69
selection = data_analysis.load_vt(args)
published = json.load(open("/mnt/e/Ciencia/noturno/2023-abbott-gwtc3-population/sources/analyses/PowerLawPeak/o1o2o3_mass_c_iid_mag_iid_tilt_powerlaw_redshift_result.json"))
posterior = pd.DataFrame(published["posterior"]["content"])
keys = published["search_parameter_keys"] + ["amax"]
rows = np.random.RandomState(2).choice(len(posterior), 12, replace=False)

def efficiency(row, alpha_chi=None, beta_chi=None):
    parameters = {key: float(posterior.iloc[row][key]) for key in keys}
    if alpha_chi is None:
        parameters, _ = convert_to_beta_parameters(parameters)
    else:
        parameters.update(alpha_chi=alpha_chi, beta_chi=beta_chi)
    return selection.detection_efficiency(parameters)[0]

correct = np.array([efficiency(row) / posterior.iloc[row]["selection"] - 1 for row in rows])
print("rel diff with each row's own alpha_chi/beta_chi:", np.round(correct, 5))

def loss(log_ab):
    a, b = np.exp(log_ab)
    return sum((efficiency(row, a, b) / posterior.iloc[row]["selection"] - 1) ** 2 for row in rows[:6])

best = minimize(loss, x0=np.log([2.0, 5.0]), method="Nelder-Mead", options=dict(xatol=1e-10, fatol=1e-28, maxiter=2000))
a, b = np.exp(best.x)
print("best single pair alpha_chi %.6f beta_chi %.6f" % (a, b))
held_out = np.array([efficiency(row, a, b) / posterior.iloc[row]["selection"] - 1 for row in rows[6:]])
print("held-out rows rel diff with that single pair:", held_out)
