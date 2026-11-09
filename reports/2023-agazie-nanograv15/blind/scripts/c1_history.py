# C1 from the hd13/3 chain recovered from git history (98a4783^), frozen rule and band
import json
import numpy as np

W = "/mnt/e/Ciencia/noturno/2023-agazie-nanograv15-cego"
SEED = 20231108
# allow_pickle stays False: plain numeric array only
chain = np.load(W + "/history/nano15_hd_chain_fg_long_050523.npy", allow_pickle=False)
print("dtype", chain.dtype, "shape", chain.shape, "finite", bool(np.all(np.isfinite(chain))))
log10_amplitude = np.ravel(chain)
print("log10A min", log10_amplitude.min(), "max", log10_amplitude.max())

# Whole array as the notebook uses it: no burn, no thinning, quantiles of log10 A then 10**
q05, q50, q95 = np.quantile(log10_amplitude, [0.05, 0.5, 0.95])
c1 = {"n": int(log10_amplitude.size), "median": 10**q50, "q05": 10**q05, "q95": 10**q95}
c1["minus"] = c1["median"] - c1["q05"]
c1["plus"] = c1["q95"] - c1["median"]
# Frozen band: rounds to printed value at 0.1e-15
c1["in_band"] = {
	"median": bool(2.35e-15 <= c1["median"] < 2.45e-15),
	"q05": bool(1.75e-15 <= c1["q05"] < 1.85e-15),
	"q95": bool(3.05e-15 <= c1["q95"] < 3.15e-15),
}
# Sensitivity, not in verdict: extra 25% burn and iid bootstrap of the three quantiles
burned = log10_amplitude[log10_amplitude.size // 4:]
c1["extra_burn25"] = [float(10**x) for x in np.quantile(burned, [0.05, 0.5, 0.95])]
rng = np.random.default_rng(SEED)
bootstrap_quantiles = np.array([np.quantile(rng.choice(log10_amplitude, log10_amplitude.size), [0.05, 0.5, 0.95]) for each_iteration in range(2000)])
c1["bootstrap_std_q05_med_q95"] = [float(np.std(10**bootstrap_quantiles[:, k])) for k in range(3)]
# Fraction near the -14 prior edge (Table 1 log-Uniform [-18, -14])
c1["log10A_range"] = [float(log10_amplitude.min()), float(log10_amplitude.max())]
print("C1", json.dumps(c1, indent=1, default=float))
json.dump(c1, open(W + "/outputs/c1_history.json", "w"), indent=1, default=float)
