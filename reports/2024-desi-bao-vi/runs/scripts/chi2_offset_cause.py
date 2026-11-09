"""Chase the constant +0.076 chi2 offset between our evaluation on the public
bao_data files and the chi2__BAO column of the authors' chain.

Candidates tested here:
  (a) their theory had dark_energy_model: ppf, ours used the default fluid;
  (b) the two chi2 columns in their chain are not the same thing;
  (c) the published text files differ from the vector their likelihood used,
      which we test by solving for the data vector offset that would close
      the gap.
"""
import numpy as np
import camb

D = "/mnt/e/Ciencia/noturno/2024-desi-bao-vi/data/official/desi-bao-all"
DATA = "/mnt/e/Ciencia/noturno/2024-desi-bao-vi/data/bao_data"
C_KMS = 299792.458
H0_FIX, OBH2_FIX = 67.36, 0.02237

with open(f"{D}/chain.1.txt") as fh:
    cols = fh.readline().lstrip("#").split()
d = np.vstack([np.loadtxt(f"{D}/chain.{i}.txt") for i in (1, 2, 3, 4)])

print("-- (b) are the two chi2 columns identical? --")
a = d[:, cols.index("chi2__BAO")]
long = [c for c in cols if c.startswith("chi2__desi_y1")][0]
b = d[:, cols.index(long)]
print(f"  max |chi2__BAO - chi2__<full name>| = {np.abs(a - b).max():.3e}")
print(f"  max |chi2 - chi2__BAO|              = "
      f"{np.abs(d[:, cols.index('chi2')] - a).max():.3e}")

z, val, kind = [], [], []
with open(f"{DATA}/desi_2024_gaussian_bao_ALL_GCcomb_mean.txt") as fh:
    for line in fh:
        if line.startswith("#") or not line.strip():
            continue
        p, q, r = line.split()
        z.append(float(p)); val.append(float(q)); kind.append(r)
z = np.array(z); val = np.array(val)
cov = np.loadtxt(f"{DATA}/desi_2024_gaussian_bao_ALL_GCcomb_cov.txt")
icov = np.linalg.inv(cov)
zu = np.array(sorted(set(z)))


def theory(omm, hrdrag, **kw):
    h = H0_FIX / 100.0
    pars = camb.set_params(H0=H0_FIX, ombh2=OBH2_FIX,
                           omch2=omm * h * h - 0.06 / 93.14 - OBH2_FIX,
                           mnu=0.06, nnu=3.044, omk=0.0, TCMB=2.7255,
                           num_massive_neutrinos=1, **kw)
    res = camb.get_background(pars)
    dm = res.comoving_radial_distance(zu) * h / hrdrag
    dh = C_KMS * h / res.hubble_parameter(zu) / hrdrag
    dv = (zu * dm ** 2 * dh) ** (1.0 / 3.0)
    t = {}
    for i, zz in enumerate(zu):
        t[(zz, "DM_over_rs")] = dm[i]
        t[(zz, "DH_over_rs")] = dh[i]
        t[(zz, "DV_over_rs")] = dv[i]
    return np.array([t[(zz, kk)] for zz, kk in zip(z, kind)])


def chi2(omm, hrdrag, **kw):
    r = val - theory(omm, hrdrag, **kw)
    return float(r @ icov @ r)


j = int(np.argmin(d[:, cols.index("chi2__BAO")]))
omm_b, rdh_b, their = (d[j, cols.index("omm")], d[j, cols.index("hrdrag")],
                       d[j, cols.index("chi2__BAO")])

print("\n-- (a) dark energy model --")
for label, kw in (("default fluid", {}),
                  ("ppf (what they used)", {"dark_energy_model": "ppf"})):
    try:
        c = chi2(omm_b, rdh_b, **kw)
        print(f"  {label:22s} chi2 = {c:.6f}  (theirs {their:.6f}, "
              f"diff {c - their:+.6f})")
    except Exception as exc:
        print(f"  {label:22s} failed: {type(exc).__name__}: {str(exc)[:70]}")

print("\n-- (c) how big a data difference would close the gap? --")
th = theory(omm_b, rdh_b)
r = val - th
print(f"  our residuals in units of the diagonal error:")
sd = np.sqrt(np.diag(cov))
for zz, kk, rr, ss in zip(z, kind, r, sd):
    print(f"    z={zz:.3f} {kk:<11s} resid {rr:+8.4f}  sigma {ss:7.4f}  "
          f"{rr/ss:+6.2f} sd")
# A uniform rescaling of the covariance that would match their chi2.
print(f"  a covariance scaled by {their / (r @ icov @ r):.5f} would reproduce "
      f"their chi2 exactly")
print(f"  i.e. their errors larger by {100*(np.sqrt((r @ icov @ r)/their)-1):+.3f}% "
      f"on average, which is at the level of a late covariance update")
