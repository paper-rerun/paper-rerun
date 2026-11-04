# Read the published PP result: priors, meta data, sampler settings and the posterior quantiles
import json
import sys
import numpy as np
result_path = sys.argv[1]
with open(result_path) as result_file:
    result = json.load(result_file)
print("top keys:", list(result.keys()))
print("priors:")
for key, value in result["priors"].items():
    print("  ", key, str(value)[:200])
meta = result.get("meta_data", {})
print("meta keys:", list(meta.keys()))
for key in ["models", "event_ids"]:
    print(key, meta.get(key))
print("n events", len(meta.get("event_ids", [])))
loaded = meta.get("loaded_modules", {})
for key in ["gwpopulation", "gwpopulation_pipe", "bilby", "dynesty", "cupy", "numpy", "scipy", "astropy"]:
    print("module", key, loaded.get(key))
for key in ["sampler_kwargs", "sampling_time", "num_likelihood_evaluations", "log_evidence", "log_evidence_err", "version", "label"]:
    print(key, str(result.get(key))[:600])
posterior = result["posterior"]["content"]
print("posterior cols", list(posterior.keys()), "n", len(posterior["mpp"]))
def quantiles(values):
    low, median, high = np.percentile(values, [5, 50, 95])
    return "median %.3f +%.3f -%.3f  [5%% %.3f, 95%% %.3f]" % (median, high - median, median - low, low, high)
mpp = np.array(posterior["mpp"])
rate = np.array(posterior["rate"])
lamb = np.array(posterior["lamb"])
print("mpp", quantiles(mpp))
print("rate z=0", quantiles(rate))
print("rate z=0.2", quantiles(rate * 1.2 ** lamb))
print("lamb", quantiles(lamb))
print("min_event_n_effective min", np.min(posterior["min_event_n_effective"]), "pdet_n_effective min", np.min(posterior["pdet_n_effective"]))
