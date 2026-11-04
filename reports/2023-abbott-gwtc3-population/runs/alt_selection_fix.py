# Alternative reading (does not change the verdict): recompute the per-sample detection efficiency with each
# sample's own alpha_chi/beta_chi (convert_to_beta_parameters applied), keep the same Gamma draw
# (N = rate * V * mu_stale), and see how much R(0.2) moves.
import json
import sys
import numpy as np
import pandas as pd
from gwpopulation_pipe import data_analysis, vt_helper
from gwpopulation.conversions import convert_to_beta_parameters

result_path = sys.argv[1]
args, _ = data_analysis.create_parser().parse_known_args(sys.argv[2:])
vt_helper.N_EVENTS = 69
selection = data_analysis.load_vt(args)
result = json.load(open(result_path))
posterior = pd.DataFrame(result["posterior"]["content"])
keys = result["search_parameter_keys"] + ["amax"]
fixed = []
for index in range(len(posterior)):
    parameters = {key: float(posterior[key].iloc[index]) for key in keys}
    parameters, _ = convert_to_beta_parameters(parameters)
    fixed.append(selection.detection_efficiency(parameters)[0])
fixed = np.array(fixed)
ratio = posterior["selection"].values / fixed
rate_fixed = posterior["rate"].values * ratio
def q(values):
    return np.percentile(values, [5, 50, 95])
print(result_path)
print("selection stale/own: median %.4f, 5%% %.4f, 95%% %.4f" % tuple(np.percentile(ratio, [50, 5, 95])))
print("R(0.2) as run   p05 %.3f p50 %.3f p95 %.3f" % tuple(q(posterior["rate"].values * 1.2 ** posterior["lamb"].values)))
print("R(0.2) own spin p05 %.3f p50 %.3f p95 %.3f" % tuple(q(rate_fixed * 1.2 ** posterior["lamb"].values)))
