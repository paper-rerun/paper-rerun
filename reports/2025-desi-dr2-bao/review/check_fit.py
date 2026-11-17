"""Attacks on fit.py, reusing only the cached CAMB output in runs/out.

  A. Reproduce C1/C2/C3 from the cached grids with my own marginaliser.
  B. Mean vs median vs mode of each marginal.
  C. Flat prior in Omega_m vs flat in omega_m = Omega_m h^2 (Jacobian 1/h^2):
     how much of C3 is the choice of sampled variable?
  D. omega_b grid widened from +/-4 sigma to +/-4.95 sigma (the r_d table's
     own range), to see whether the 3.6e-5 edge mass matters.
  E. Grid refinement: halve the grid by taking every other point.
  F. The same BAO-alone fit with a covariance built from Table IV instead of
     the released one, to test the report's claim that agreement with the
     published sigmas shows the paper used the release.
"""
import numpy as np
from scipy.interpolate import RectBivariateSpline

ROOT = "/mnt/e/Ciencia/noturno/2025-desi-dr2-bao"
OUT = f"{ROOT}/runs/out"
DATA = f"{ROOT}/data"
C_KMS = 299792.458

z, val, kind = [], [], []
with open(f"{DATA}/desi_dr2_gaussian_bao_ALL_GCcomb_mean.txt") as fh:
    for line in fh:
        if line.startswith("#") or not line.strip():
            continue
        a, b, c = line.split()
        z.append(float(a)); val.append(float(b)); kind.append(c)
Z, VAL = np.array(z), np.array(val)
COV = np.loadtxt(f"{DATA}/desi_dr2_gaussian_bao_ALL_GCcomb_cov.txt")
ZU = np.array(sorted(set(Z)))
ZIDX = np.array([int(np.where(ZU == zz)[0][0]) for zz in Z])
IS_DM = np.array([k == "DM_over_rs" for k in kind])
IS_DH = np.array([k == "DH_over_rs" for k in kind])
IS_DV = np.array([k == "DV_over_rs" for k in kind])

T4_SIG = {(0.295, "DV_over_rs"): 0.075,
          (0.510, "DM_over_rs"): 0.167, (0.510, "DH_over_rs"): 0.425,
          (0.706, "DM_over_rs"): 0.177, (0.706, "DH_over_rs"): 0.330,
          (0.934, "DM_over_rs"): 0.152, (0.934, "DH_over_rs"): 0.193,
          (1.321, "DM_over_rs"): 0.318, (1.321, "DH_over_rs"): 0.221,
          (1.484, "DM_over_rs"): 0.760, (1.484, "DH_over_rs"): 0.516,
          (2.330, "DM_over_rs"): 0.531, (2.330, "DH_over_rs"): 0.101}
T4_CORR = {0.510: -0.459, 0.706: -0.404, 0.934: -0.416,
           1.321: -0.434, 1.484: -0.500, 2.330: -0.431}


def table4_cov():
    s = np.array([T4_SIG[(zz, kk)] for zz, kk in zip(Z, kind)])
    c = np.diag(s ** 2)
    for zz, r in T4_CORR.items():
        i, j = [k for k in range(len(Z)) if Z[k] == zz]
        c[i, j] = c[j, i] = r * s[i] * s[j]
    return c


def chi2(dm_h, dh_h, rdh, icov):
    dm = dm_h / rdh[..., None]
    dh = dh_h / rdh[..., None]
    dv = (ZU * dm ** 2 * dh) ** (1.0 / 3.0)
    th = np.empty(dm.shape[:-1] + (len(Z),))
    th[..., IS_DM] = dm[..., ZIDX[IS_DM]]
    th[..., IS_DH] = dh[..., ZIDX[IS_DH]]
    th[..., IS_DV] = dv[..., ZIDX[IS_DV]]
    d = VAL - th
    return np.einsum("...i,ij,...j->...", d, icov, d)


def summarise(p, x):
    """mean, sigma, median, mode of a 1D weight array on a regular grid."""
    p = p / p.sum()
    mean = float((p * x).sum())
    sig = float(np.sqrt((p * (x - mean) ** 2).sum()))
    cdf = np.cumsum(p)
    med = float(np.interp(0.5, cdf, x))
    mode = float(x[int(p.argmax())])
    return mean, sig, med, mode, float(p[0] + p[-1])


def marg1(logp, i, x, weight=None):
    p = np.exp(logp - logp.max())
    if weight is not None:
        p = p * weight
    others = tuple(j for j in range(p.ndim) if j != i)
    return summarise(p.sum(axis=others), x)


# ------------------------------------------------------------------ stage C --
dc = np.load(f"{OUT}/dist_c.npz")
OM_C, HS = dc["oms"], dc["hs"]
RDH_C = np.linspace(90.0, 115.0, 701)
ih = int(np.argmin(np.abs(HS - 0.68)))
dm = np.broadcast_to(dc["dm_h"][ih][:, None, :], (len(OM_C), len(RDH_C), len(ZU)))
dh = np.broadcast_to(dc["dh_h"][ih][:, None, :], dm.shape)
rdh = np.broadcast_to(RDH_C[None, :], (len(OM_C), len(RDH_C)))

print("== A/B. BAO alone, released covariance ==")
for icov, tag in ((np.linalg.inv(COV), "released"),
                  (np.linalg.inv(table4_cov()), "Table IV")):
    c2 = chi2(dm, dh, rdh, icov)
    lp = -0.5 * c2
    for i, (nm, x) in enumerate((("Omega_m", OM_C), ("rd_h", RDH_C))):
        me, sg, md, mo, ed = marg1(lp, i, x)
        print(f"  [{tag:8s}] {nm:8s} mean {me:.6f} sig {sg:.6f} "
              f"median {md:.6f} mode {mo:.6f} edge {ed:.1e}")
    print(f"  [{tag:8s}] chi2_min {c2.min():.4f}")
    # flat prior in omega_m = Omega_m * h^2 instead of Omega_m. At fixed rd_h
    # h is not a grid axis here, so use h = 0.68 -> constant Jacobian: no shift.
print("  (BAO alone: reparametrising Omega_m -> Omega_m h^2 at fixed h is a"
      " constant Jacobian, so it cannot shift this marginal)")

print("\n== E. BAO alone on half the grid (every other point) ==")
icov = np.linalg.inv(COV)
c2 = chi2(dm[::2, ::2], dh[::2, ::2], rdh[::2, ::2], icov)
for i, (nm, x) in enumerate((("Omega_m", OM_C[::2]), ("rd_h", RDH_C[::2]))):
    me, sg, md, mo, ed = marg1(-0.5 * c2, i, x)
    print(f"  {nm:8s} mean {me:.6f} sig {sg:.6f}")

# ------------------------------------------------------------------ stage D --
dd = np.load(f"{OUT}/dist_d.npz")
OM_D, HSD = dd["oms"], dd["hs"]
H0_D = HSD * 100.0
tab = np.load(f"{OUT}/rd_table.npz")
spl = RectBivariateSpline(tab["ob"], tab["om2"], tab["rd"], kx=3, ky=3)
OB_BBN, OB_SIG = 0.02218, 0.00055


def stage_d(ob_grid, sub=1, weight_mode="flat_Om"):
    om_d, h0_d = OM_D[::sub], H0_D[::sub]
    hs = h0_d / 100.0
    dm_all = dd["dm_h"][::sub, ::sub, :]
    dh_all = dd["dh_h"][::sub, ::sub, :]
    om2 = np.broadcast_to((om_d[None, :, None] * (hs ** 2)[:, None, None]),
                          (len(h0_d), len(om_d), len(ob_grid)))
    obg = np.broadcast_to(ob_grid[None, None, :], om2.shape)
    rdh = spl.ev(obg, om2) * hs[:, None, None]
    dmb = np.broadcast_to(dm_all[:, :, None, :],
                          (len(h0_d), len(om_d), len(ob_grid), len(ZU)))
    dhb = np.broadcast_to(dh_all[:, :, None, :], dmb.shape)
    c2 = chi2(dmb, dhb, rdh, np.linalg.inv(COV))
    c2 = c2 + ((ob_grid - OB_BBN) / OB_SIG) ** 2
    lp = -0.5 * c2
    w = None
    if weight_mode == "flat_om_h2":          # flat in omega_m = Omega_m h^2
        w = np.broadcast_to((1.0 / hs ** 2)[:, None, None], c2.shape)
    elif weight_mode == "flat_h_rd":         # flat in h, fine already; test 1/h
        w = np.broadcast_to((1.0 / hs)[:, None, None], c2.shape)
    out = {}
    for i, (nm, x) in enumerate((("H0", h0_d), ("Omega_m", om_d),
                                 ("omega_b", ob_grid))):
        out[nm] = marg1(lp, i, x, w)
    out["chi2_min"] = float(c2.min())
    return out


OB_BASE = np.linspace(0.0200, 0.0244, 61)
OB_WIDE = np.linspace(0.0195, 0.0249, 121)
print("\n== A/B/C/D. BAO + BBN ==")
for tag, ob, sub, wm in (("baseline", OB_BASE, 1, "flat_Om"),
                         ("ob wide +/-4.95sig", OB_WIDE, 1, "flat_Om"),
                         ("half grid", OB_BASE, 2, "flat_Om"),
                         ("flat in Om*h^2", OB_BASE, 1, "flat_om_h2"),
                         ("flat in 1/h", OB_BASE, 1, "flat_h_rd")):
    r = stage_d(ob, sub, wm)
    print(f"  [{tag:18s}] chi2_min {r['chi2_min']:.4f}")
    for nm in ("H0", "Omega_m", "omega_b"):
        me, sg, md, mo, ed = r[nm]
        print(f"      {nm:8s} mean {me:.6f} sig {sg:.6f} median {md:.6f} "
              f"mode {mo:.6f} edge {ed:.1e}")
