# Blind rerun of NANOGrav 15yr GWB claims from the repo's presampled cores
# Follows the frozen claims.json (sha256 in claims.json.sha256)
import json
import sys

import numpy as np

W = "/mnt/e/Ciencia/noturno/2023-agazie-nanograv15-cego"
CORES = W + "/repo/tutorials/presampled_cores"
SEED = 20231108
GAMMA_13_3 = 13.0 / 3.0

from la_forge import core, slices

sys.path.insert(0, W + "/repo/tutorials")
import extra_functions

results = {}


def quantiles_of_amplitude(log10_amplitude_samples):
	# Median and 5-95% of A, not of log10 A (quantiles commute with the monotone map)
	q05, q50, q95 = np.quantile(log10_amplitude_samples, [0.05, 0.5, 0.95])
	return {"median": 10**q50, "q05": 10**q05, "q95": 10**q95}


def describe_core(name, loaded_core):
	info = {
		"params_count": len(loaded_core.params),
		"chain_shape": list(np.shape(loaded_core.chain)),
		"burn": int(loaded_core.burn) if loaded_core.burn is not None else None,
		"first_params": list(loaded_core.params[:5]),
		"last_params": list(loaded_core.params[-6:]),
	}
	print(name, json.dumps(info))
	return info


# ---- P1 and E1: varied-gamma HD chain
hd_pl_core = core.Core(corepath=CORES + "/hd_14f_pl_vg.core")
results["hd_14f_pl_vg_info"] = describe_core("hd_14f_pl_vg", hd_pl_core)
gw_params = [p for p in hd_pl_core.params if p.startswith("gw")]
print("gw params:", gw_params)
log10_amplitude = hd_pl_core.get_param("gw__log10_A")
gamma = hd_pl_core.get_param("gw__gamma")
number_of_samples = len(gamma)
print("samples after burn:", number_of_samples)

# P1: product identity check against Sec. 3 varied-gamma numbers
p1 = quantiles_of_amplitude(log10_amplitude)
gamma_q05, gamma_q50, gamma_q95 = np.quantile(gamma, [0.05, 0.5, 0.95])
p1.update({"gamma_median": gamma_q50, "gamma_q05": gamma_q05, "gamma_q95": gamma_q95, "n": number_of_samples})
p1["fraction_gamma_above_13_3"] = float(np.mean(gamma > GAMMA_13_3))
p1["log10A_min"] = float(log10_amplitude.min())
p1["log10A_max"] = float(log10_amplitude.max())
p1["gamma_min"] = float(gamma.min())
p1["gamma_max"] = float(gamma.max())
results["P1"] = p1
print("P1", json.dumps(p1))


def slice_estimate(log10_amplitude_all, gamma_all, half_width, adjust):
	# Samples near gamma = 13/3, optionally regression-adjusted to gamma = 13/3
	in_window = np.abs(gamma_all - GAMMA_13_3) < half_width
	window_count = int(in_window.sum())
	if window_count < 3:
		return {"half_width": half_width, "adjust": adjust, "n": window_count}
	delta_gamma = gamma_all[in_window] - GAMMA_13_3
	window_log10_amplitude = log10_amplitude_all[in_window]
	slope = 0.0
	if adjust:
		slope, intercept = np.polyfit(delta_gamma, window_log10_amplitude, 1)
		window_log10_amplitude = window_log10_amplitude - slope * delta_gamma
	estimate = quantiles_of_amplitude(window_log10_amplitude)
	estimate.update({
		"half_width": half_width,
		"adjust": adjust,
		"n": window_count,
		"slope_dlog10A_dgamma": float(slope),
		"fraction_log10A_above_minus14": float(np.mean(window_log10_amplitude > -14.0)),
	})
	return estimate


e1 = {"primary": slice_estimate(log10_amplitude, gamma, 0.15, True), "sensitivity": []}
for half_width in [0.05, 0.10, 0.15, 0.20]:
	e1["sensitivity"].append(slice_estimate(log10_amplitude, gamma, half_width, False))
for half_width in [0.10, 0.20]:
	e1["sensitivity"].append(slice_estimate(log10_amplitude, gamma, half_width, True))

# Extra 25% burn-in on top of the core's own
extra_burn = number_of_samples // 4
burned = slice_estimate(log10_amplitude[extra_burn:], gamma[extra_burn:], 0.15, True)
burned["note"] = "extra 25% burn"
e1["sensitivity"].append(burned)

# Bootstrap of the primary median (iid resampling of the whole chain)
rng = np.random.default_rng(SEED)
bootstrap_medians = []
for each_iteration in range(2000):
	resample_index = rng.integers(0, number_of_samples, number_of_samples)
	each_estimate = slice_estimate(log10_amplitude[resample_index], gamma[resample_index], 0.15, True)
	if each_estimate["n"] >= 3:
		bootstrap_medians.append(each_estimate["median"])
bootstrap_medians = np.array(bootstrap_medians)
e1["bootstrap_median_mean"] = float(bootstrap_medians.mean())
e1["bootstrap_median_std"] = float(bootstrap_medians.std())
e1["bootstrap_median_q16_q84"] = [float(x) for x in np.quantile(bootstrap_medians, [0.16, 0.84])]
results["E1"] = e1
print("E1", json.dumps(e1, indent=1))

# ---- C2: HyperModel product-space BF hd vs curn
hyper_core = core.Core(corepath=CORES + "/curn_hd.core")
results["curn_hd_info"] = describe_core("curn_hd", hyper_core)
print("curn_hd gw params:", [p for p in hyper_core.params if p.startswith("gw") or p == "nmodel"])
nmodel = hyper_core.get_param("nmodel")
CURN_LOG_WEIGHT_FACTOR = 300.0
curn_count = int(np.sum(nmodel <= 0.5))
hd_count = int(np.sum(nmodel > 0.5))
bayes_factor_hd_curn = hd_count / curn_count * CURN_LOG_WEIGHT_FACTOR
rng = np.random.default_rng(SEED)
iid_bootstrap = []
for each_iteration in range(2000):
	resampled = rng.choice(nmodel, len(nmodel))
	iid_bootstrap.append(np.sum(resampled > 0.5) / np.sum(resampled <= 0.5) * CURN_LOG_WEIGHT_FACTOR)
BLOCK_LENGTH = 1000
block_count = len(nmodel) // BLOCK_LENGTH
blocks = nmodel[:block_count * BLOCK_LENGTH].reshape(block_count, BLOCK_LENGTH)
block_bootstrap = []
for each_iteration in range(2000):
	resampled = blocks[rng.integers(0, block_count, block_count)].ravel()
	block_bootstrap.append(np.sum(resampled > 0.5) / np.sum(resampled <= 0.5) * CURN_LOG_WEIGHT_FACTOR)
# Number of model switches tells how well the index mixes
switch_count = int(np.sum(np.diff((nmodel > 0.5).astype(int)) != 0))
c2 = {
	"n": int(len(nmodel)), "hd_count": hd_count, "curn_count": curn_count,
	"nmodel_min": float(nmodel.min()), "nmodel_max": float(nmodel.max()),
	"BF": bayes_factor_hd_curn,
	"iid_bootstrap_mean": float(np.mean(iid_bootstrap)), "iid_bootstrap_std": float(np.std(iid_bootstrap)),
	"block1000_bootstrap_std": float(np.std(block_bootstrap)), "blocks": block_count,
	"model_switches": switch_count,
}
# Extra 25% burn
nmodel_burned = nmodel[len(nmodel) // 4:]
c2["BF_extra_burn25"] = float(np.sum(nmodel_burned > 0.5) / np.sum(nmodel_burned <= 0.5) * CURN_LOG_WEIGHT_FACTOR)
results["C2"] = c2
print("C2", json.dumps(c2))

# ---- C3, C4, C5: thermodynamic integration
extra_functions.rng = np.random.default_rng(SEED)
ti_cores = {}
for model_name in ["irn", "curn", "hd"]:
	ti_cores[model_name] = slices.SlicesCore(corepath=CORES + "/{0}_ti.core".format(model_name))
	each_core = ti_cores[model_name]
	temps = sorted(float(p) for p in each_core.params)
	print(model_name, "temps:", len(temps), "min", temps[0], "max", temps[-1], "chain shape", np.shape(each_core.chain))
	results[model_name + "_ti_info"] = {"temps": len(temps), "Tmin": temps[0], "Tmax": temps[-1], "chain_shape": list(np.shape(each_core.chain))}

authors_ln_evidence = {}
for model_name in ["irn", "curn", "hd"]:
	ln_evidence, ln_evidence_unc = extra_functions.ti_log_evidence(ti_cores[model_name], verbose=False)
	authors_ln_evidence[model_name] = (float(ln_evidence), float(ln_evidence_unc))


def plain_trapezoid_ln_evidence(slices_core):
	# Mean lnlike per temperature, trapezoid over beta, no sorting, no bootstrap
	temps = np.array(sorted(float(p) for p in slices_core.params))
	betas = 1.0 / temps[::-1]
	mean_lnlike = np.array([np.mean(slices_core.get_param(str(t))) for t in temps[::-1]])
	main_part = np.trapz(mean_lnlike, betas)
	# Missing piece from beta = 0 to beta_min, as a rectangle
	missing_part = betas[0] * mean_lnlike[0]
	return float(main_part), float(missing_part)


plain_ln_evidence = {m: plain_trapezoid_ln_evidence(ti_cores[m]) for m in ["irn", "curn", "hd"]}
LN10 = np.log(10.0)


def log10_bayes_factor(numerator, denominator, source):
	if source == "authors":
		value = (authors_ln_evidence[numerator][0] - authors_ln_evidence[denominator][0]) / LN10
		unc = np.hypot(authors_ln_evidence[numerator][1], authors_ln_evidence[denominator][1]) / LN10
		return {"log10_BF": float(value), "unc": float(unc)}
	value = (plain_ln_evidence[numerator][0] - plain_ln_evidence[denominator][0]) / LN10
	return {"log10_BF": float(value)}


results["ti_ln_evidence_authors_fn"] = authors_ln_evidence
results["ti_ln_evidence_plain_trapz"] = plain_ln_evidence
results["C3"] = {"authors_fn": log10_bayes_factor("curn", "irn", "authors"), "plain": log10_bayes_factor("curn", "irn", "plain")}
results["C4"] = {"authors_fn": log10_bayes_factor("hd", "irn", "authors"), "plain": log10_bayes_factor("hd", "irn", "plain")}
c5_authors = log10_bayes_factor("hd", "curn", "authors")
c5_plain = log10_bayes_factor("hd", "curn", "plain")
c5_authors["BF"] = float(10**c5_authors["log10_BF"])
c5_authors["BF_1sigma"] = [float(10**(c5_authors["log10_BF"] - c5_authors["unc"])), float(10**(c5_authors["log10_BF"] + c5_authors["unc"]))]
c5_plain["BF"] = float(10**c5_plain["log10_BF"])
results["C5"] = {"authors_fn": c5_authors, "plain": c5_plain}
for claim_id in ["C3", "C4", "C5"]:
	print(claim_id, json.dumps(results[claim_id]))

json.dump(results, open(W + "/outputs/results.json", "w"), indent=1, default=float)
print("wrote outputs/results.json")
