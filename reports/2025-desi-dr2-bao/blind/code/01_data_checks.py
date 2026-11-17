# Guard checks on the DESI DR2 data release before any fitting
import json, hashlib, os, sys
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import load_data, MEAN_FILE, COV_FILE, ROOT

# Table IV of arXiv:2503.14738v3, the seven tracers used for cosmology
TABLE_IV = {
    (0.295, "DV_over_rs"): (7.942, 0.075),
    (0.510, "DM_over_rs"): (13.588, 0.167),
    (0.510, "DH_over_rs"): (21.863, 0.425),
    (0.706, "DM_over_rs"): (17.351, 0.177),
    (0.706, "DH_over_rs"): (19.455, 0.330),
    (0.934, "DM_over_rs"): (21.576, 0.152),
    (0.934, "DH_over_rs"): (17.641, 0.193),
    (1.321, "DM_over_rs"): (27.601, 0.318),
    (1.321, "DH_over_rs"): (14.176, 0.221),
    (1.484, "DM_over_rs"): (30.512, 0.760),
    (1.484, "DH_over_rs"): (12.817, 0.516),
    (2.330, "DM_over_rs"): (38.988, 0.531),
    (2.330, "DH_over_rs"): (8.632, 0.101),
}
# correlation coefficients r_M,H from Table IV, keyed by z
TABLE_IV_RMH = {0.510: -0.459, 0.706: -0.404, 0.934: -0.416,
                1.321: -0.434, 1.484: -0.500, 2.330: -0.431}

z, d, kinds, cov = load_data()
out = {"n_data": len(d)}

for name, path in (("mean", MEAN_FILE), ("cov", COV_FILE)):
    out[name + "_sha256"] = hashlib.sha256(open(path, "rb").read()).hexdigest()

# --- data vector against Table IV, entry by entry
sig = np.sqrt(np.diag(cov))
rows = []
worst_val = 0.0
worst_sig = 0.0
for i in range(len(d)):
    key = (round(z[i], 3), kinds[i])
    pv, ps = TABLE_IV[key]
    dv = abs(d[i] - pv)
    ds = abs(sig[i] - ps)
    worst_val = max(worst_val, dv)
    worst_sig = max(worst_sig, ds)
    rows.append({"i": i, "z": z[i], "quantity": kinds[i],
                 "file_value": d[i], "paper_value": pv, "abs_diff": dv,
                 "file_sigma": sig[i], "paper_sigma": ps, "abs_diff_sigma": ds})
out["table_iv_comparison"] = rows
# the paper rounds to 3 decimals on values and sigmas, so half a unit in the last
# printed digit is the most agreement we can ask for
out["table_iv_max_abs_diff_value"] = worst_val
out["table_iv_max_abs_diff_sigma"] = worst_sig
out["table_iv_values_match_to_paper_rounding"] = bool(worst_val <= 0.0005)
out["table_iv_sigmas_match_to_paper_rounding"] = bool(worst_sig <= 0.0005)

# --- correlation coefficients of the DM/DH pairs
rmh = {}
for i in range(len(d) - 1):
    if kinds[i] == "DM_over_rs" and kinds[i + 1] == "DH_over_rs" and z[i] == z[i + 1]:
        rmh[str(round(z[i], 3))] = cov[i, i + 1] / (sig[i] * sig[i + 1])
# the Lya block is stored DH first, DM second
for i in range(len(d) - 1):
    if kinds[i] == "DH_over_rs" and kinds[i + 1] == "DM_over_rs" and z[i] == z[i + 1]:
        rmh[str(round(z[i], 3))] = cov[i, i + 1] / (sig[i] * sig[i + 1])
out["corr_DM_DH_from_cov"] = rmh
out["corr_DM_DH_from_table_iv"] = {str(k): v for k, v in TABLE_IV_RMH.items()}
out["corr_max_abs_diff"] = max(abs(rmh[str(k)] - v) for k, v in TABLE_IV_RMH.items())

# --- covariance sanity
out["cov_max_asymmetry"] = float(np.max(np.abs(cov - cov.T)))
ev = np.linalg.eigvalsh(cov)
out["cov_min_eigenvalue"] = float(ev.min())
out["cov_max_eigenvalue"] = float(ev.max())
out["cov_condition_number"] = float(ev.max() / ev.min())
try:
    np.linalg.cholesky(cov)
    out["cov_positive_definite"] = True
except np.linalg.LinAlgError:
    out["cov_positive_definite"] = False
# block structure: how many off-diagonal entries are exactly zero
off = cov[~np.eye(len(d), dtype=bool)]
out["cov_offdiag_exact_zeros"] = int(np.sum(off == 0.0))
out["cov_offdiag_total"] = int(off.size)

os.makedirs(os.path.join(ROOT, "out"), exist_ok=True)
with open(os.path.join(ROOT, "out", "data_checks.json"), "w") as f:
    json.dump(out, f, indent=2)
print(json.dumps({k: v for k, v in out.items() if k != "table_iv_comparison"}, indent=2))
for r in rows:
    print("z=%6.3f %-12s file=%12.8f paper=%8.3f d=%.2e | sig file=%9.6f paper=%6.3f d=%.2e"
          % (r["z"], r["quantity"], r["file_value"], r["paper_value"], r["abs_diff"],
             r["file_sigma"], r["paper_sigma"], r["abs_diff_sigma"]))
