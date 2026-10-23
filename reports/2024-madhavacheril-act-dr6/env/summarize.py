# Print mean +- std of the target parameters for a set of Cobaya chains
# usage: python summarize.py <chain_root> [ignore_rows]
import sys
import numpy as np
from getdist import loadMCSamples

chain_root = sys.argv[1]
ignore_rows = float(sys.argv[2]) if len(sys.argv) > 2 else 0.3
samples = loadMCSamples(chain_root, settings={"ignore_rows": ignore_rows})
# S8^CMBL is derived as S825 in the authors' yaml; recompute so it also works on any chain
samples.addDerived(samples.getParams().sigma8 * (samples.getParams().omegam / 0.3) ** 0.25, name="S8CMBL_check")
samples.addDerived(samples.getParams().sigma8 * (samples.getParams().omegam / 0.3) ** 0.5, name="S8_check")
all_names = [p.name for p in samples.getParamNames().names]
weights = samples.weights
print(chain_root, "ignore_rows =", ignore_rows)
print("rows =", len(weights), " sum(w) =", round(weights.sum(), 1), " (sum w)^2/sum(w^2) =", round(weights.sum() ** 2 / (weights ** 2).sum(), 1))
print("R-1 (getdist, worst eigenvalue of sampled params):", samples.getGelmanRubin())

# Per-parameter R-1: variance of the chain means over the mean of the chain variances
chain_offsets = samples.chain_offsets


def per_parameter_rminus1(param_index):
	chain_means = []
	chain_variances = []
	for chain_number in range(len(chain_offsets) - 1):
		start_row = chain_offsets[chain_number]
		end_row = chain_offsets[chain_number + 1]
		chain_weights = weights[start_row:end_row]
		chain_values = samples.samples[start_row:end_row, param_index]
		if chain_weights.sum() <= 0:
			continue
		chain_mean = np.average(chain_values, weights=chain_weights)
		chain_means.append(chain_mean)
		chain_variances.append(np.average((chain_values - chain_mean) ** 2, weights=chain_weights))
	if len(chain_means) < 2:
		return float("nan")
	return np.var(chain_means, ddof=1) / np.mean(chain_variances)


for name in ["S8CMBL_check", "S825", "sigma8", "S8_check", "omegam", "H0"]:
	if name in all_names:
		param_index = all_names.index(name)
		print(f"{name:14s} mean = {samples.mean(name):.4f}  std = {samples.std(name):.4f}  R-1(this param) = {per_parameter_rminus1(param_index):.4f}")
