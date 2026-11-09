# Diagnose why plain trapezoid TI differs from the authors' ti_log_evidence
# Also list non-pulsar params of the HyperModel core (is gamma varied?)
import json

import numpy as np
from scipy.integrate import simpson
from scipy.interpolate import interp1d
from la_forge import core, slices

W = "/mnt/e/Ciencia/noturno/2023-agazie-nanograv15-cego"
CORES = W + "/repo/tutorials/presampled_cores"
LN10 = np.log(10.0)

hyper_core = core.Core(corepath=CORES + "/curn_hd.core")
print("curn_hd non-pulsar params:", [p for p in hyper_core.params if "+" not in p and "-" not in p])
print("curn_hd params containing gamma but not red_noise:", [p for p in hyper_core.params if "gamma" in p and "red_noise" not in p])
hd_pl_core = core.Core(corepath=CORES + "/hd_14f_pl_vg.core")
print("hd_14f_pl_vg non-pulsar params:", [p for p in hd_pl_core.params if "+" not in p and "-" not in p])

diagnostic = {}
for model_name in ["irn", "curn", "hd"]:
	each_core = slices.SlicesCore(corepath=CORES + "/{0}_ti.core".format(model_name))
	temps = np.array(sorted(float(p) for p in each_core.params))
	betas = 1.0 / temps[::-1]
	mean_lnlike = np.array([np.mean(each_core.get_param(str(t))) for t in temps[::-1]])
	# Plain trapezoid in beta
	trapz_beta = np.trapz(mean_lnlike, betas)
	# Authors' quadrature (linear interp in log10 beta, Simpson in beta), no bootstrap, no sort
	log10_betas = np.log10(betas)
	fine_log10_betas = np.linspace(log10_betas[0], log10_betas[-1], num=10000)
	authors_quadrature = simpson(interp1d(log10_betas, mean_lnlike)(fine_log10_betas), 10**fine_log10_betas)
	# Same with sorted means (the authors force monotonicity)
	authors_quadrature_sorted = simpson(interp1d(log10_betas, np.sort(mean_lnlike))(fine_log10_betas), 10**fine_log10_betas)
	# Trapezoid in beta but only over the ladder above beta = 1e-7
	diagnostic[model_name] = {
		"betas": betas.tolist(),
		"mean_lnlike": mean_lnlike.tolist(),
		"is_monotonic": bool(np.all(np.diff(mean_lnlike) >= 0)),
		"trapz_beta": float(trapz_beta),
		"authors_quadrature_no_bootstrap": float(authors_quadrature),
		"authors_quadrature_sorted_no_bootstrap": float(authors_quadrature_sorted),
		"samples_per_temp": int(len(each_core.get_param(str(temps[0])))),
	}
	print(model_name, "monotonic:", diagnostic[model_name]["is_monotonic"], "trapz:", trapz_beta, "authors quad:", authors_quadrature, "sorted:", authors_quadrature_sorted)
	print("  top 6 betas:", np.round(betas[-6:], 5).tolist())
	print("  top 6 <lnL>:", np.round(mean_lnlike[-6:], 2).tolist())
	print("  low 4 betas:", betas[:4].tolist(), "<lnL>:", np.round(mean_lnlike[:4], 2).tolist())

for numerator, denominator in [("curn", "irn"), ("hd", "irn"), ("hd", "curn")]:
	for key in ["trapz_beta", "authors_quadrature_no_bootstrap", "authors_quadrature_sorted_no_bootstrap"]:
		print(numerator, "vs", denominator, key, "log10 BF =", (diagnostic[numerator][key] - diagnostic[denominator][key]) / LN10)
json.dump(diagnostic, open(W + "/outputs/ti_diagnostic.json", "w"), indent=1)
