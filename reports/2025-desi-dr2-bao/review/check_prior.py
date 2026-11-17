"""Two more attacks, on the cached grids only.

  G. The 68% minimal credible interval of our H0 marginal, and its skewness:
     the paper quotes mean+sigma only when the marginal is symmetric.
  H. Does the DR2 test actually discriminate between the two BBN priors the
     paper prints? Redo C3 with eq. (15), omega_b h^2 = 0.02196 +/- 0.00063,
     the Neff-varying prior that caused the DR1 offset.
  I. The Omega_m - rd*h correlation of the BAO-alone grid (paper: r = -0.92).
"""
import numpy as np
from scipy.interpolate import RectBivariateSpline

ROOT = "/mnt/e/Ciencia/noturno/2025-desi-dr2-bao"
OUT, DATA = f"{ROOT}/runs/out", f"{ROOT}/data"

z, val, kind = [], [], []
with open(f"{DATA}/desi_dr2_gaussian_bao_ALL_GCcomb_mean.txt") as fh:
    for line in fh:
        if line.startswith("#") or not line.strip():
            continue
        a, b, c = line.split()
        z.append(float(a)); val.append(float(b)); kind.append(c)
Z, VAL = np.array(z), np.array(val)
ICOV = np.linalg.inv(np.loadtxt(f"{DATA}/desi_dr2_gaussian_bao_ALL_GCcomb_cov.txt"))
ZU = np.array(sorted(set(Z)))
ZIDX = np.array([int(np.where(ZU == zz)[0][0]) for zz in Z])
IS_DM = np.array([k == "DM_over_rs" for k in kind])
IS_DH = np.array([k == "DH_over_rs" for k in kind])
IS_DV = np.array([k == "DV_over_rs" for k in kind])


def chi2(dm_h, dh_h, rdh):
    dm = dm_h / rdh[..., None]
    dh = dh_h / rdh[..., None]
    dv = (ZU * dm ** 2 * dh) ** (1.0 / 3.0)
    th = np.empty(dm.shape[:-1] + (len(Z),))
    th[..., IS_DM] = dm[..., ZIDX[IS_DM]]
    th[..., IS_DH] = dh[..., ZIDX[IS_DH]]
    th[..., IS_DV] = dv[..., ZIDX[IS_DV]]
    d = VAL - th
    return np.einsum("...i,ij,...j->...", d, ICOV, d)


def minimal_interval(p, x, level=0.68):
    """Shortest interval holding `level` of the mass, highest density first."""
    p = p / p.sum()
    order = np.argsort(p)[::-1]
    keep = np.zeros_like(p, dtype=bool)
    tot = 0.0
    for i in order:
        keep[i] = True
        tot += p[i]
        if tot >= level:
            break
    xs = x[keep]
    return float(xs.min()), float(xs.max())


dd = np.load(f"{OUT}/dist_d.npz")
OM_D, HS = dd["oms"], dd["hs"]
H0_D = HS * 100.0
tab = np.load(f"{OUT}/rd_table.npz")
spl = RectBivariateSpline(tab["ob"], tab["om2"], tab["rd"], kx=3, ky=3)


def run(ob_mu, ob_sig, ob_grid):
    om2 = np.broadcast_to(OM_D[None, :, None] * (HS ** 2)[:, None, None],
                          (len(H0_D), len(OM_D), len(ob_grid)))
    obg = np.broadcast_to(ob_grid[None, None, :], om2.shape)
    rdh = spl.ev(obg, om2) * HS[:, None, None]
    dm = np.broadcast_to(dd["dm_h"][:, :, None, :],
                         (len(H0_D), len(OM_D), len(ob_grid), len(ZU)))
    dh = np.broadcast_to(dd["dh_h"][:, :, None, :], dm.shape)
    c2 = chi2(dm, dh, rdh) + ((ob_grid - ob_mu) / ob_sig) ** 2
    p = np.exp(-0.5 * (c2 - c2.min()))
    m = p.sum(axis=(1, 2)); m /= m.sum()
    mean = float((m * H0_D).sum())
    sig = float(np.sqrt((m * (H0_D - mean) ** 2).sum()))
    skew = float((m * (H0_D - mean) ** 3).sum() / sig ** 3)
    lo, hi = minimal_interval(m, H0_D)
    q16 = float(np.interp(0.16, np.cumsum(m), H0_D))
    q84 = float(np.interp(0.84, np.cumsum(m), H0_D))
    return mean, sig, skew, lo, hi, q16, q84, float(m[0] + m[-1])


print("== G. H0 marginal, baseline BBN prior eq. (14) 0.02218 +/- 0.00055 ==")
mean, sig, skew, lo, hi, q16, q84, edge = run(
    0.02218, 0.00055, np.linspace(0.0200, 0.0244, 61))
print(f"  mean {mean:.4f}  std {sig:.4f}  skewness {skew:+.4f}")
print(f"  68% minimal interval [{lo:.4f}, {hi:.4f}] -> half width "
      f"{(hi - lo) / 2:.4f}, centre {(hi + lo) / 2:.4f}")
print(f"  16-84 percentiles [{q16:.4f}, {q84:.4f}] -> half width "
      f"{(q84 - q16) / 2:.4f}")
print(f"  published: 68.51 +/- 0.58 (mean and standard deviation per Sec. V)")

print("\n== H. same fit with the Neff-varying BBN prior, eq. (15) ==")
m2, s2, sk2, lo2, hi2, a, b, e2 = run(0.02196, 0.00063,
                                      np.linspace(0.01980, 0.02412, 61))
print(f"  H0 mean {m2:.4f} +/- {s2:.4f}   shift vs published "
      f"{(m2 - 68.51) / 0.58:+.3f} sigma   (band is +/-0.20 sigma)")
print(f"  eq. (14) gave {mean:.4f} ({(mean - 68.51) / 0.58:+.3f} sigma)")
print(f"  both priors inside the pre-registered band: "
      f"{abs(m2 - 68.51) / 0.58 < 0.2 and abs(mean - 68.51) / 0.58 < 0.2}")

print("\n== I. Omega_m - rd*h correlation, BAO alone ==")
dc = np.load(f"{OUT}/dist_c.npz")
OM_C, HSC = dc["oms"], dc["hs"]
RDH = np.linspace(90.0, 115.0, 701)
ih = int(np.argmin(np.abs(HSC - 0.68)))
dm = np.broadcast_to(dc["dm_h"][ih][:, None, :], (len(OM_C), len(RDH), len(ZU)))
dh = np.broadcast_to(dc["dh_h"][ih][:, None, :], dm.shape)
c2 = chi2(dm, dh, np.broadcast_to(RDH[None, :], (len(OM_C), len(RDH))))
p = np.exp(-0.5 * (c2 - c2.min())); p /= p.sum()
mo = (p.sum(1) * OM_C).sum(); mr = (p.sum(0) * RDH).sum()
so = np.sqrt((p.sum(1) * (OM_C - mo) ** 2).sum())
sr = np.sqrt((p.sum(0) * (RDH - mr) ** 2).sum())
cross = (p * (OM_C[:, None] - mo) * (RDH[None, :] - mr)).sum()
print(f"  r = {cross / (so * sr):+.4f}   (paper: -0.92)")

print("\n== H2. the exact DR1-style sliced prior, 0.021976 +/- 0.000534 ==")
m3, s3, sk3, lo3, hi3, a3, b3, e3 = run(
    0.021976, 0.000534, np.linspace(0.019840, 0.024112, 61))
print(f"  H0 mean {m3:.4f} +/- {s3:.4f}   shift vs published "
      f"{(m3 - 68.51) / 0.58:+.3f} sigma")
