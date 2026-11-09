"""Their BAO-alone chain reports a best chi2__BAO of 12.661; our grid minimum
is 12.738. Either our grid is too coarse, or our data/covariance differ from
the ones their internal likelihood used. Evaluate OUR chi2 at THEIR exact
parameter values and see which."""
import numpy as np
import camb

D = "/mnt/e/Ciencia/noturno/2024-desi-bao-vi/data/official/desi-bao-all"
DATA = "/mnt/e/Ciencia/noturno/2024-desi-bao-vi/data/bao_data"
C_KMS = 299792.458
# Fixed in their chain.updated.yaml for this run.
H0_FIX, OBH2_FIX = 67.36, 0.02237

with open(f"{D}/chain.1.txt") as fh:
    cols = fh.readline().lstrip("#").split()
d = np.vstack([np.loadtxt(f"{D}/chain.{i}.txt") for i in (1, 2, 3, 4)])

z, val, kind = [], [], []
with open(f"{DATA}/desi_2024_gaussian_bao_ALL_GCcomb_mean.txt") as fh:
    for line in fh:
        if line.startswith("#") or not line.strip():
            continue
        a, b, c = line.split()
        z.append(float(a)); val.append(float(b)); kind.append(c)
z = np.array(z); val = np.array(val)
cov = np.loadtxt(f"{DATA}/desi_2024_gaussian_bao_ALL_GCcomb_cov.txt")
icov = np.linalg.inv(cov)
zu = np.array(sorted(set(z)))


def our_chi2(omm, hrdrag):
    h = H0_FIX / 100.0
    omch2 = omm * h * h - 0.06 / 93.14 - OBH2_FIX
    pars = camb.set_params(H0=H0_FIX, ombh2=OBH2_FIX, omch2=omch2, mnu=0.06,
                           nnu=3.044, omk=0.0, TCMB=2.7255,
                           num_massive_neutrinos=1)
    res = camb.get_background(pars)
    dm = res.comoving_radial_distance(zu) * h / hrdrag
    dh = C_KMS * h / res.hubble_parameter(zu) / hrdrag
    dv = (zu * dm ** 2 * dh) ** (1.0 / 3.0)
    t = {}
    for i, zz in enumerate(zu):
        t[(zz, "DM_over_rs")] = dm[i]
        t[(zz, "DH_over_rs")] = dh[i]
        t[(zz, "DV_over_rs")] = dv[i]
    th = np.array([t[(zz, kk)] for zz, kk in zip(z, kind)])
    r = val - th
    return float(r @ icov @ r), th


ic = cols.index("chi2__BAO")
j = int(np.argmin(d[:, ic]))
omm_b, rdh_b, chi2_b = (d[j, cols.index("omm")], d[j, cols.index("hrdrag")],
                        d[j, ic])
print(f"their best sample: omm={omm_b:.6f}, r_d h={rdh_b:.5f}, "
      f"their chi2__BAO={chi2_b:.5f}")
ours, th = our_chi2(omm_b, rdh_b)
print(f"our chi2 at that exact point: {ours:.5f}  "
      f"(difference {ours - chi2_b:+.5f})")

# Minimise our chi2 properly, so "grid too coarse" is ruled out.
from scipy.optimize import minimize
r = minimize(lambda p: our_chi2(p[0], p[1])[0], [0.2947, 101.9],
             method="Nelder-Mead",
             options={"xatol": 1e-7, "fatol": 1e-9, "maxiter": 2000})
print(f"\nour true minimum: chi2={r.fun:.5f} at omm={r.x[0]:.6f}, "
      f"r_d h={r.x[1]:.5f}")
print(f"our grid minimum was 12.7383, so the grid is off by "
      f"{12.7383 - r.fun:.5f} in chi2")
print(f"gap to their chain's best chi2__BAO: {r.fun - chi2_b:+.5f}")

# Spread of their chi2__BAO at fixed parameters would show a data difference.
print("\n-- is the gap a constant offset? their chi2__BAO vs ours on 300 "
      "random samples --")
rng = np.random.default_rng(1)
pick = rng.choice(len(d), 300, replace=False)
diffs = []
for i in pick:
    o, _ = our_chi2(d[i, cols.index("omm")], d[i, cols.index("hrdrag")])
    diffs.append(o - d[i, ic])
diffs = np.array(diffs)
print(f"  ours - theirs: mean {diffs.mean():+.5f}, sd {diffs.std():.5f}, "
      f"min {diffs.min():+.5f}, max {diffs.max():+.5f}")
print("  a near-constant offset with tiny scatter means the same theory but a "
      "different data vector or covariance;")
print("  a scatter that grows with chi2 would mean a theory difference.")
