# Build the likelihood exactly as gwpopulation_pipe main() does, then evaluate it at published
# posterior samples and compare with the published log_likelihood, selection and surveyed_hypervolume
# columns. Also times one likelihood evaluation.
import json
import sys
import time
import numpy as np
import pandas as pd
from gwpopulation_pipe import data_analysis, vt_helper
from gwpopulation.cupy_utils import xp

run_dir = sys.argv[1]
argv = sys.argv[2:]
args, _ = data_analysis.create_parser().parse_known_args(argv)
posteriors = pd.read_pickle(run_dir + "/data/posteriors.pkl")
for index, post in enumerate(posteriors):
    posteriors[index] = post[post["redshift"] < args.max_redshift]
vt_helper.N_EVENTS = len(posteriors)
hyper_prior = data_analysis.load_prior(args)
model = data_analysis.load_model(args)
selection = data_analysis.load_vt(args)
likelihood = data_analysis.create_likelihood(args, posteriors, model, selection)
print("backend", xp.__name__, "n_events", vt_helper.N_EVENTS, "n found injections", len(selection.data["mass_1"]),
      "analysis_time", selection.data.get("analysis_time"), "total_generated", selection.data.get("total_generated"))

published = json.load(open("/mnt/e/Ciencia/noturno/2023-abbott-gwtc3-population/sources/analyses/PowerLawPeak/o1o2o3_mass_c_iid_mag_iid_tilt_powerlaw_redshift_result.json"))
posterior = pd.DataFrame(published["posterior"]["content"])
keys = published["search_parameter_keys"] + ["amax"]
order = np.argsort(posterior["log_likelihood"].values)[::-1]
picks = list(order[:5]) + list(np.random.RandomState(1).choice(len(posterior), 15, replace=False))
max_diff_ll = 0
max_rel_sel = 0
max_rel_vol = 0
for pick in picks:
    row = posterior.iloc[pick]
    likelihood.parameters.update({key: float(row[key]) for key in keys})
    log_l = likelihood.log_likelihood_ratio()
    parameters = {key: float(row[key]) for key in keys}
    efficiency, variance = selection.detection_efficiency(parameters)
    volume = float(selection.surveyed_hypervolume(parameters))
    max_diff_ll = max(max_diff_ll, abs(log_l - row["log_likelihood"]))
    max_rel_sel = max(max_rel_sel, abs(float(efficiency) / row["selection"] - 1))
    max_rel_vol = max(max_rel_vol, abs(volume / row["surveyed_hypervolume"] - 1))
    print("sample %5d  logL ours %.6f published %.6f  diff %.2e | selection rel diff %.2e | volume rel diff %.2e" % (
        pick, log_l, row["log_likelihood"], log_l - row["log_likelihood"],
        float(efficiency) / row["selection"] - 1, volume / row["surveyed_hypervolume"] - 1))
print("MAX |dlogL| %.3e  MAX rel selection %.3e  MAX rel volume %.3e" % (max_diff_ll, max_rel_sel, max_rel_vol))

# Timing
row = posterior.iloc[order[0]]
likelihood.parameters.update({key: float(row[key]) for key in keys})
likelihood.log_likelihood_ratio()
start = time.time()
for _ in range(50):
    sample = hyper_prior.sample()
    likelihood.parameters.update(sample)
    likelihood.log_likelihood_ratio()
print("seconds per likelihood evaluation (random prior draws): %.4f" % ((time.time() - start) / 50))
