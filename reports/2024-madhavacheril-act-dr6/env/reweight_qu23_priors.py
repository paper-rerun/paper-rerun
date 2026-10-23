# Reweight a lens-only chain from the Madhavacheril+24 Table 1 priors to the ones in
# Qu+24 Table "priors" (logA in [2,4], ombh2 ~ N(0.0223, 0.0005)), to see whether the
# prior difference explains 0.816 (public chain) vs 0.818 (Qu+24 text)
# usage: python reweight_qu23_priors.py <chain_root> [ignore_rows]
import sys
import numpy as np
from getdist import loadMCSamples

chain_root = sys.argv[1]
ignore_rows = float(sys.argv[2]) if len(sys.argv) > 2 else 0.3
samples = loadMCSamples(chain_root, settings={"ignore_rows": ignore_rows})
params = samples.getParams()
s8cmbl = params.sigma8 * (params.omegam / 0.3) ** 0.25


def gaussian_density(values, mean, sigma):
	return np.exp(-0.5 * ((values - mean) / sigma) ** 2) / sigma


# Ratio of the new prior to the one the chain was sampled with
ombh2_ratio = gaussian_density(params.ombh2, 0.0223, 0.0005) / gaussian_density(params.ombh2, 0.02233, 0.00036)
loga_inside_new_range = (params.logA >= 2.0) & (params.logA <= 4.0)
new_weights = samples.weights * ombh2_ratio * loga_inside_new_range

for label, chain_weights in [("Table 1 priors (as sampled)", samples.weights), ("Qu+24 priors (reweighted)", new_weights)]:
	mean = np.average(s8cmbl, weights=chain_weights)
	std = np.sqrt(np.average((s8cmbl - mean) ** 2, weights=chain_weights))
	effective_samples = chain_weights.sum() ** 2 / (chain_weights ** 2).sum()
	print(f"{label:28s} S8CMBL = {mean:.4f} +- {std:.4f}   (sum w)^2/sum(w^2) = {effective_samples:.0f}")
print("fraction of weight with logA < 2:", round(float(samples.weights[params.logA < 2.0].sum() / samples.weights.sum()), 4))
