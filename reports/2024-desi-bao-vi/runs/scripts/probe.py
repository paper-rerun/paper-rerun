"""Triage probe, run before the fits.

Three things only:
  1. The data vector we read has to equal Table 1 of the paper.
  2. Our distance definitions have to agree with CAMB's own, which is the point
     of using CAMB at all.
  3. How long one CAMB background call costs, so we can size the grids.
"""
import time
import numpy as np
import camb

DATA = "/mnt/e/Ciencia/noturno/2024-desi-bao-vi/data/bao_data"
C_KMS = 299792.458

# Table 1 of arXiv:2404.03002, typed from the printed table, 2 decimals.
TABLE1 = [
    (0.295, 7.93, "DV_over_rs"),
    (0.510, 13.62, "DM_over_rs"), (0.510, 20.98, "DH_over_rs"),
    (0.706, 16.85, "DM_over_rs"), (0.706, 20.08, "DH_over_rs"),
    (0.930, 21.71, "DM_over_rs"), (0.930, 17.88, "DH_over_rs"),
    (1.317, 27.79, "DM_over_rs"), (1.317, 13.82, "DH_over_rs"),
    (1.491, 26.07, "DV_over_rs"),
    (2.330, 39.71, "DM_over_rs"), (2.330, 8.52, "DH_over_rs"),
]


def load():
    z, val, kind = [], [], []
    with open(f"{DATA}/desi_2024_gaussian_bao_ALL_GCcomb_mean.txt") as fh:
        for line in fh:
            if line.startswith("#") or not line.strip():
                continue
            a, b, c = line.split()
            z.append(float(a)); val.append(float(b)); kind.append(c)
    cov = np.loadtxt(f"{DATA}/desi_2024_gaussian_bao_ALL_GCcomb_cov.txt")
    return np.array(z), np.array(val), kind, cov


def main():
    z, val, kind, cov = load()
    print(f"n_data = {len(val)}, cov shape = {cov.shape}")
    assert cov.shape == (len(val), len(val))
    assert np.allclose(cov, cov.T), "covariance is not symmetric"
    ev = np.linalg.eigvalsh(cov)
    print(f"cov eigenvalues: min {ev.min():.6e} max {ev.max():.6e}")
    assert ev.min() > 0, "covariance is not positive definite"

    print("\n-- check 1: data vector against Table 1 of the paper --")
    bad = 0
    for (zt, vt, kt), zr, vr, kr in zip(TABLE1, z, val, kind):
        ok = (abs(zt - zr) < 1e-9) and (kt == kr) and (abs(vt - vr) < 0.005)
        bad += not ok
        print(f"  z={zr:.3f} {kr:<11s} file {vr:9.5f}  table {vt:7.2f}  "
              f"{'ok' if ok else 'MISMATCH'}")
    print(f"  mismatches: {bad}")

    print("\n-- check 2: our distance definitions against CAMB --")
    # A reference cosmology near the paper's own best fit.
    h, om, ob = 0.6853, 0.295, 0.02218
    pars = camb.set_params(H0=100 * h, ombh2=ob, omch2=0.12, mnu=0.06,
                           nnu=3.044, omk=0.0, TCMB=2.7255)
    omnuh2 = pars.omnuh2
    pars = camb.set_params(H0=100 * h, ombh2=ob,
                           omch2=om * h * h - ob - omnuh2,
                           mnu=0.06, nnu=3.044, omk=0.0, TCMB=2.7255)
    res = camb.get_background(pars)
    print(f"  omnuh2 from CAMB for mnu=0.06: {omnuh2:.8f}")
    print(f"  requested Omega_m {om:.6f}, CAMB pars.omegam {pars.omegam:.6f}, "
          f"diff {pars.omegam - om:+.2e}")
    rd = res.get_derived_params()["rdrag"]
    print(f"  r_drag = {rd:.4f} Mpc, r_d h = {rd * h:.4f} Mpc")

    zs = np.array(sorted(set(z)))
    # CAMB's own angular diameter distance, converted to comoving transverse.
    dm_camb = res.angular_diameter_distance(zs) * (1 + zs)
    dm_ours = res.comoving_radial_distance(zs)          # flat, so D_M = chi
    rel = np.abs(dm_ours / dm_camb - 1)
    for zz, a, b, r in zip(zs, dm_ours, dm_camb, rel):
        print(f"  z={zz:.3f}  D_M chi {a:10.4f}  (1+z)D_A {b:10.4f}  "
              f"rel {r:.2e}")
    print(f"  worst relative difference: {rel.max():.3e}")

    # And the predicted observables at this reference point, with chi-square.
    dh = C_KMS / res.hubble_parameter(zs)
    dv = (zs * dm_camb ** 2 * dh) ** (1.0 / 3.0)
    pred = {}
    for zz, a, b, c in zip(zs, dm_camb, dh, dv):
        pred[(zz, "DM_over_rs")] = a / rd
        pred[(zz, "DH_over_rs")] = b / rd
        pred[(zz, "DV_over_rs")] = c / rd
    theory = np.array([pred[(zz, kk)] for zz, kk in zip(z, kind)])
    d = val - theory
    chi2 = d @ np.linalg.solve(cov, d)
    print(f"\n-- check 3: chi-square at the reference cosmology --")
    print(f"  chi2 = {chi2:.3f} for {len(val)} data points and 2 fitted "
          f"parameters (dof ~ {len(val) - 2})")
    for zz, kk, o, t in zip(z, kind, val, theory):
        print(f"  z={zz:.3f} {kk:<11s} data {o:9.4f}  theory {t:9.4f}  "
              f"({100 * (t / o - 1):+.2f}%)")

    print("\n-- timing --")
    t0 = time.perf_counter()
    n = 20
    for i in range(n):
        p = camb.set_params(H0=68.0 + 0.01 * i, ombh2=ob, omch2=0.12,
                            mnu=0.06, nnu=3.044, omk=0.0, TCMB=2.7255)
        r = camb.get_background(p)
        r.comoving_radial_distance(zs)
        r.hubble_parameter(zs)
    print(f"  background only, no rdrag: {1e3 * (time.perf_counter() - t0) / n:.1f} ms/call")
    t0 = time.perf_counter()
    for i in range(n):
        p = camb.set_params(H0=68.0 + 0.01 * i, ombh2=ob, omch2=0.12,
                            mnu=0.06, nnu=3.044, omk=0.0, TCMB=2.7255)
        r = camb.get_background(p)
        r.get_derived_params()["rdrag"]
    print(f"  with rdrag: {1e3 * (time.perf_counter() - t0) / n:.1f} ms/call")


if __name__ == "__main__":
    main()
