# Grid marginalisation for C1, C2 (BAO alone) and C3 (BAO + BBN omega_b prior)
import json, os, sys
import numpy as np
from scipy.interpolate import RectBivariateSpline
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import load_data, ROOT

WB_MEAN, WB_SIG = 0.02218, 0.00055   # eq. (14) of the paper

z, d, kinds, cov = load_data()
Cinv = np.linalg.inv(cov)
T = np.load(os.path.join(ROOT, "out", "theory_tables.npz"))
om_grid, A_tab = T["om_grid"], T["A_tab"]
rd_spline = RectBivariateSpline(T["wb_tab"], T["wm_tab"], np.log(T["rd_tab"]), kx=3, ky=3)


def quad_coeffs(A):
    """chi2(x) = a0 - 2*a1/x + a2/x^2 with x = h*rd, model = A/x"""
    Cid = Cinv @ d
    return float(d @ Cid), A @ Cid, np.einsum("...i,ij,...j->...", A, Cinv, A)


a0 = float(d @ Cinv @ d)
a1 = A_tab @ (Cinv @ d)
a2 = np.einsum("ni,ij,nj->n", A_tab, Cinv, A_tab)


def moments(grid, w):
    w = w / w.sum()
    m = float((grid * w).sum())
    s = float(np.sqrt(((grid - m) ** 2 * w).sum()))
    return m, s, float(w[0]), float(w[-1])


res = {}

# ---------------- C1 / C2 : flat priors on Omega_m and x = h*rd ----------------
x_grid = np.linspace(95.0, 108.0, 651)
chi2 = a0 - 2.0 * a1[:, None] / x_grid[None, :] + a2[:, None] / x_grid[None, :] ** 2
chi2_min = chi2.min()
post = np.exp(-0.5 * (chi2 - chi2_min))
m_om, s_om, e0_om, e1_om = moments(om_grid, post.sum(axis=1))
m_x, s_x, e0_x, e1_x = moments(x_grid, post.sum(axis=0))
P = post / post.sum()
cov_ox = float((P * np.outer(om_grid - m_om, x_grid - m_x)).sum())
ij = np.unravel_index(np.argmin(chi2), chi2.shape)
res["C1_C2"] = {
    "Omega_m_mean": m_om, "Omega_m_sigma": s_om,
    "h_rd_mean_Mpc": m_x, "h_rd_sigma_Mpc": s_x,
    "correlation_Omega_m_h_rd": cov_ox / (s_om * s_x),
    "chi2_min": float(chi2_min), "n_data": len(d), "n_params": 2,
    "dof": len(d) - 2,
    "bestfit_Omega_m_on_grid": float(om_grid[ij[0]]),
    "bestfit_h_rd_on_grid": float(x_grid[ij[1]]),
    "edge_mass_Omega_m": [e0_om, e1_om],
    "edge_mass_h_rd": [e0_x, e1_x],
}

# ---------------- C3 : BAO + BBN prior on omega_b ----------------
om3 = np.linspace(0.230, 0.370, 141)
assert np.allclose(om3, om_grid[::2])
a1_3, a2_3 = a1[::2], a2[::2]
H0_grid = np.linspace(63.0, 74.0, 441)
wb_grid = np.linspace(0.0180, 0.0264, 169)
h = H0_grid / 100.0
wm = om3[:, None] * h[None, :] ** 2            # (nom, nH0)
wb_prior = np.exp(-0.5 * ((wb_grid - WB_MEAN) / WB_SIG) ** 2)

acc = np.zeros((len(om3), len(H0_grid), len(wb_grid)))
for k, wb in enumerate(wb_grid):
    rd = np.exp(rd_spline.ev(np.full(wm.shape, wb), wm))
    x = h[None, :] * rd
    c2 = a0 - 2.0 * a1_3[:, None] / x + a2_3[:, None] / x ** 2
    acc[:, :, k] = c2
c2min = acc.min()
post3 = np.exp(-0.5 * (acc - c2min)) * wb_prior[None, None, :]
mH, sH, e0H, e1H = moments(H0_grid, post3.sum(axis=(0, 2)))
mO, sO, e0O, e1O = moments(om3, post3.sum(axis=(1, 2)))
mW, sW, e0W, e1W = moments(wb_grid, post3.sum(axis=(0, 1)))
ijk = np.unravel_index(np.argmin(acc), acc.shape)
res["C3"] = {
    "H0_mean": mH, "H0_sigma": sH,
    "Omega_m_mean": mO, "Omega_m_sigma": sO,
    "omega_b_mean": mW, "omega_b_sigma": sW,
    "chi2_min_over_grid": float(c2min),
    "bestfit_Omega_m_on_grid": float(om3[ijk[0]]),
    "bestfit_H0_on_grid": float(H0_grid[ijk[1]]),
    "edge_mass_H0": [e0H, e1H],
    "edge_mass_Omega_m": [e0O, e1O],
    "edge_mass_omega_b": [e0W, e1W],
    "bbn_prior": {"mean": WB_MEAN, "sigma": WB_SIG, "source": "eq. (14)"},
}

# ---------------- pre-registered tolerance ----------------
published = {"C1": (0.2975, 0.0086, res["C1_C2"]["Omega_m_mean"], res["C1_C2"]["Omega_m_sigma"]),
             "C2": (101.54, 0.73, res["C1_C2"]["h_rd_mean_Mpc"], res["C1_C2"]["h_rd_sigma_Mpc"]),
             "C3": (68.51, 0.58, res["C3"]["H0_mean"], res["C3"]["H0_sigma"])}
verdict = {}
for cid, (pm, ps, mm, ms) in published.items():
    dm, ds = abs(mm - pm), abs(ms - ps)
    verdict[cid] = {"published_mean": pm, "published_sigma": ps,
                    "my_mean": mm, "my_sigma": ms,
                    "mean_offset_in_published_sigma": dm / ps,
                    "sigma_ratio": ms / ps,
                    "mean_ok": bool(dm <= 0.20 * ps),
                    "sigma_ok": bool(ds <= 0.10 * ps)}
    verdict[cid]["pass"] = bool(verdict[cid]["mean_ok"] and verdict[cid]["sigma_ok"])
res["verdict"] = verdict
npass = sum(v["pass"] for v in verdict.values())
res["overall"] = ("Reproduced" if npass == 3 else
                  "Partially reproduced" if npass >= 1 else "Not reproduced")

# edge-mass gate
all_edges = (res["C1_C2"]["edge_mass_Omega_m"] + res["C1_C2"]["edge_mass_h_rd"] +
             res["C3"]["edge_mass_H0"] + res["C3"]["edge_mass_Omega_m"] + res["C3"]["edge_mass_omega_b"])
res["max_edge_mass"] = max(all_edges)
res["grid_valid"] = bool(res["max_edge_mass"] < 1e-6)

with open(os.path.join(ROOT, "out", "fit_results.json"), "w") as f:
    json.dump(res, f, indent=2)
print(json.dumps(res, indent=2))
