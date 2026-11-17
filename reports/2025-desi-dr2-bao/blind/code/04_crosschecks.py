# Cross-checks: (a) my chi2 vs cobaya own released BAO likelihood at the same cosmology,
#               (b) r_d interpolation table error vs direct CAMB calls
import json, os, sys
import numpy as np
from scipy.interpolate import RectBivariateSpline
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import load_data, model_A, camb_background, MEAN_FILE, COV_FILE, ROOT

z, d, kinds, cov = load_data()
Cinv = np.linalg.inv(cov)
out = {}

# ---------- (a) cobaya cross-check ----------
TEST = [(0.2975, 0.6851, 0.02218), (0.31, 0.67, 0.0224), (0.28, 0.70, 0.0220)]
from cobaya.model import get_model
import cobaya
out["cobaya_version"] = cobaya.__version__

rows = []
for om, h, wb in TEST:
    _, omnuh2, rd = camb_background(om, h=h, omega_b=wb)
    omch2 = om * h * h - wb - omnuh2
    info = {
        "likelihood": {"bao.generic": {"measurements_file": MEAN_FILE, "cov_file": COV_FILE}},
        "theory": {"camb": {"extra_args": {"num_massive_neutrinos": 1, "nnu": 3.044,
                                           "TCMB": 2.7255, "halofit_version": "mead"}}},
        "params": {"ombh2": wb, "omch2": omch2, "H0": 100.0 * h, "mnu": 0.06,
                   "ns": 0.965, "As": 2.1e-9, "tau": 0.054},
    }
    model = get_model(info)
    logp = model.loglike({}, return_derived=False)
    chi2_cobaya = -2.0 * float(logp)

    # mine, at exactly the same cosmology, using the same CAMB background
    A, rd_mine = model_A(z, kinds, om, h=h, omega_b=wb)
    m = A / (h * rd_mine)
    r = d - m
    chi2_mine = float(r @ Cinv @ r)
    rows.append({"Omega_m": om, "h": h, "omega_b": wb, "rdrag_Mpc": rd,
                 "chi2_cobaya": chi2_cobaya, "chi2_mine": chi2_mine,
                 "abs_diff": abs(chi2_cobaya - chi2_mine)})
    print(rows[-1])
out["cobaya_chi2_comparison"] = rows
out["cobaya_chi2_max_abs_diff"] = max(r_["abs_diff"] for r_ in rows)

# ---------- (b) r_d table accuracy ----------
T = np.load(os.path.join(ROOT, "out", "theory_tables.npz"))
spl = RectBivariateSpline(T["wb_tab"], T["wm_tab"], np.log(T["rd_tab"]), kx=3, ky=3)
rng = np.random.default_rng(20261117)
errs = []
for _ in range(20):
    wb = float(rng.uniform(0.0185, 0.0259))
    wm = float(rng.uniform(0.095, 0.205))
    hh = 0.70
    _, _, rd_direct = camb_background(wm / hh ** 2, h=hh, omega_b=wb)
    rd_interp = float(np.exp(spl.ev(wb, wm)))
    errs.append(abs(rd_interp - rd_direct) / rd_direct)
out["rd_interp_max_rel_error"] = float(max(errs))
out["rd_interp_mean_rel_error"] = float(np.mean(errs))
out["rd_interp_n_test_points"] = len(errs)

# ---------- (c) scaling identity: model really is A/x ----------
A1, rd1 = model_A(z, kinds, 0.2975, h=0.65, omega_b=0.02218)
A2, rd2 = model_A(z, kinds, 0.2975, h=0.72, omega_b=0.02218)
out["A_identity_max_rel_diff_h065_vs_h072"] = float(np.max(np.abs(A2 - A1) / A1))

with open(os.path.join(ROOT, "out", "crosschecks.json"), "w") as f:
    json.dump(out, f, indent=2)
print(json.dumps({k: v for k, v in out.items() if k != "cobaya_chi2_comparison"}, indent=2))
