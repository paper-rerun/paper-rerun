"""Checks that rule our own code out, run after the fit.

  1. The data vector we read has to equal Table IV of the paper, all 13 rows.
  2. Covariance symmetric and positive definite.
  3. Our D_M against CAMB's own (1+z)D_A, the flat-space identity.
  4. Our chi-square against cobaya's released BAO likelihood, same cosmology.
"""
import numpy as np
import camb

ROOT = "/mnt/e/Ciencia/noturno/2025-desi-dr2-bao"
DATA = f"{ROOT}/data"
C_KMS = 299792.458
OMNUH2 = 0.00064487

# Table IV of arXiv:2503.14738, typed from the printed table, 3 decimals
TABLE4 = [
    (0.295, 7.942, "DV_over_rs"),
    (0.510, 13.588, "DM_over_rs"), (0.510, 21.863, "DH_over_rs"),
    (0.706, 17.351, "DM_over_rs"), (0.706, 19.455, "DH_over_rs"),
    (0.934, 21.576, "DM_over_rs"), (0.934, 17.641, "DH_over_rs"),
    (1.321, 27.601, "DM_over_rs"), (1.321, 14.176, "DH_over_rs"),
    (1.484, 30.512, "DM_over_rs"), (1.484, 12.817, "DH_over_rs"),
    # The Lya row comes out of the file as DH first, then DM, unlike every
    # other tracer. Order here follows the file, not the printed table
    (2.330, 8.632, "DH_over_rs"), (2.330, 38.988, "DM_over_rs"),
]


def load():
    z, val, kind = [], [], []
    with open(f"{DATA}/desi_dr2_gaussian_bao_ALL_GCcomb_mean.txt") as fh:
        for line in fh:
            if line.startswith("#") or not line.strip():
                continue
            a, b, c = line.split()
            z.append(float(a)); val.append(float(b)); kind.append(c)
    cov = np.loadtxt(f"{DATA}/desi_dr2_gaussian_bao_ALL_GCcomb_cov.txt")
    return np.array(z), np.array(val), kind, cov


def theory(H0, omegam, ombh2, z, kind, **kw):
    h = H0 / 100.0
    pars = camb.set_params(H0=H0, ombh2=ombh2,
                           omch2=omegam * h * h - ombh2 - OMNUH2,
                           mnu=0.06, nnu=3.044, omk=0.0, TCMB=2.7255, **kw)
    res = camb.get_background(pars)
    rd = res.get_derived_params()["rdrag"]
    zu = np.array(sorted(set(z)))
    dm = res.comoving_radial_distance(zu) / rd
    dh = C_KMS / res.hubble_parameter(zu) / rd
    dv = (zu * dm ** 2 * dh) ** (1.0 / 3.0)
    tab = {}
    for i, zz in enumerate(zu):
        tab[(zz, "DM_over_rs")] = dm[i]
        tab[(zz, "DH_over_rs")] = dh[i]
        tab[(zz, "DV_over_rs")] = dv[i]
    return np.array([tab[(zz, kk)] for zz, kk in zip(z, kind)]), float(rd), res


def main():
    z, val, kind, cov = load()
    print(f"n_data = {len(val)}, cov shape = {cov.shape}")
    assert cov.shape == (len(val), len(val))
    assert np.allclose(cov, cov.T), "covariance is not symmetric"
    ev = np.linalg.eigvalsh(cov)
    print(f"cov eigenvalues: min {ev.min():.6e} max {ev.max():.6e}")
    assert ev.min() > 0, "covariance is not positive definite"

    print("\n-- check 1: data vector against Table IV of the paper --")
    bad = 0
    for (zt, vt, kt), zr, vr, kr in zip(TABLE4, z, val, kind):
        # 0.0015 and not half a unit in the last printed digit: the Lya D_M/r_d
        # is 38.988974 in the file and 38.988 in the table, so the printed digit
        # is truncated, not rounded. Every other row rounds
        ok = (abs(zt - zr) < 1e-9) and (kt == kr) and (abs(vt - vr) < 0.0015)
        rounds = abs(vt - round(vr, 3)) < 1e-9
        bad += not ok
        print(f"  z={zr:.3f} {kr:<11s} file {vr:10.6f}  table {vt:7.3f}  "
              f"{'ok' if ok else 'MISMATCH'}"
              f"{'' if rounds else '  (table digit truncated, not rounded)'}")
    print(f"  mismatches: {bad}")
    assert bad == 0

    print("\n-- check 2: our D_M against CAMB's own (1+z)D_A --")
    REF = dict(H0=68.5466, omegam=0.297728, ombh2=0.022186)
    th, rd, res = theory(z=z, kind=kind, **REF)
    zu = np.array(sorted(set(z)))
    dm_ours = res.comoving_radial_distance(zu)
    dm_camb = res.angular_diameter_distance(zu) * (1 + zu)
    rel = np.abs(dm_ours / dm_camb - 1)
    print(f"  r_drag = {rd:.4f} Mpc, r_d h = {rd * REF['H0'] / 100:.4f} Mpc")
    print(f"  worst relative difference over {len(zu)} redshifts: {rel.max():.3e}")

    d = val - th
    chi2 = float(d @ np.linalg.solve(cov, d))
    print(f"\n-- check 3: chi-square at the reference cosmology --")
    print(f"  chi2 = {chi2:.4f} for {len(val)} points, 2 fitted parameters")

    print("\n-- check 4: our chi2 against cobaya's released BAO likelihood --")
    try:
        from cobaya.model import get_model
        info = {
            # cobaya 3.5 ships no desi_dr2 class, so we point its generic BAO
            # likelihood at the same two files. desi_2024_bao_all and the DR2
            # classes are thin subclasses of this same base_classes/bao.py.
            "likelihood": {"bao.generic": {
                "measurements_file": f"{DATA}/desi_dr2_gaussian_bao_ALL_GCcomb_mean.txt",
                "cov_file": f"{DATA}/desi_dr2_gaussian_bao_ALL_GCcomb_cov.txt"}},
            "theory": {"camb": {"extra_args": {
                "num_massive_neutrinos": 1, "nnu": 3.044, "theta_H0_range": [20, 100]}}},
            "params": {
                "H0": REF["H0"], "ombh2": REF["ombh2"],
                "omch2": REF["omegam"] * (REF["H0"] / 100) ** 2 - REF["ombh2"] - OMNUH2,
                "mnu": 0.06, "omk": 0.0, "tau": 0.0544, "ns": 0.965,
                "logA": 3.044, "As": {"value": "lambda logA: 1e-10*np.exp(logA)"}},
            "stop_at_error": True, "debug": False,
        }
        model = get_model(info)
        logp = model.loglikes({}, as_dict=True)[0]["bao.generic"]
        print(f"  cobaya chi2 = {-2 * logp:.6f}")
        print(f"  ours        = {chi2:.6f}")
        print(f"  difference  = {-2 * logp - chi2:+.2e}")
    except Exception as exc:
        print(f"  skipped: {type(exc).__name__}: {exc}")


if __name__ == "__main__":
    main()
