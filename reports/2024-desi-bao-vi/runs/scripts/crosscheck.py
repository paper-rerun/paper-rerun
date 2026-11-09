"""Cross-checks run after the grid fits, to find out whether the +0.20 sigma
offset on H0 is our code or the paper.

1. Our chi-square against cobaya's own bao.desi_2024_bao_all likelihood at the
   same cosmology. This checks our data handling and our theory vector against
   the authors' released likelihood code.
2. How much r_drag moves with CAMB's accuracy settings and recombination model,
   since H0 from BAO+BBN is just (r_d h)*100/r_d and a 0.1% error in r_d is a
   0.1% error in H0.
"""
import numpy as np
import camb
from cobaya.model import get_model

ROOT = "/mnt/e/Ciencia/noturno/2024-desi-bao-vi"
OMNUH2 = 0.00064487
REF = dict(H0=68.6912, omegam=0.295186, ombh2=0.022186)


def ours(H0, omegam, ombh2, **kw):
    import json
    h = H0 / 100.0
    pars = camb.set_params(H0=H0, ombh2=ombh2,
                           omch2=omegam * h * h - ombh2 - OMNUH2,
                           mnu=0.06, nnu=3.044, omk=0.0, TCMB=2.7255, **kw)
    res = camb.get_background(pars)
    rd = res.get_derived_params()["rdrag"]
    z, val, kind = [], [], []
    with open(f"{ROOT}/data/bao_data/desi_2024_gaussian_bao_ALL_GCcomb_mean.txt") as fh:
        for line in fh:
            if line.startswith("#") or not line.strip():
                continue
            a, b, c = line.split()
            z.append(float(a)); val.append(float(b)); kind.append(c)
    z = np.array(z); val = np.array(val)
    cov = np.loadtxt(f"{ROOT}/data/bao_data/desi_2024_gaussian_bao_ALL_GCcomb_cov.txt")
    zu = np.array(sorted(set(z)))
    dm = res.comoving_radial_distance(zu) / rd
    dh = 299792.458 / res.hubble_parameter(zu) / rd
    dv = (zu * dm ** 2 * dh) ** (1.0 / 3.0)
    tab = {}
    for i, zz in enumerate(zu):
        tab[(zz, "DM_over_rs")] = dm[i]
        tab[(zz, "DH_over_rs")] = dh[i]
        tab[(zz, "DV_over_rs")] = dv[i]
    th = np.array([tab[(zz, kk)] for zz, kk in zip(z, kind)])
    d = val - th
    return float(d @ np.linalg.solve(cov, d)), float(rd)


def main():
    print("== 1. our chi2 vs cobaya's own DESI DR1 likelihood ==")
    info = {
        # cobaya 3.5 (the version contemporary with the paper) does not yet
        # ship the desi_2024_bao_all class, so we point cobaya's generic BAO
        # likelihood at the same two DESI DR1 files. desi_2024_bao_all is a
        # thin subclass of this same base_classes/bao.py code, so this still
        # exercises the authors' released likelihood, not ours.
        "likelihood": {"bao.generic": {
            "measurements_file": f"{ROOT}/data/bao_data/"
                                 "desi_2024_gaussian_bao_ALL_GCcomb_mean.txt",
            "cov_file": f"{ROOT}/data/bao_data/"
                        "desi_2024_gaussian_bao_ALL_GCcomb_cov.txt",
            "rs_fid": 1.0,
        }},
        "theory": {"camb": {"extra_args": {"num_massive_neutrinos": 1,
                                           "nnu": 3.044, "mnu": 0.06,
                                           "TCMB": 2.7255}}},
        "params": {
            "H0": REF["H0"],
            "omegam": REF["omegam"],
            "ombh2": REF["ombh2"],
            "omch2": {"value": "lambda omegam, ombh2, H0: "
                               f"omegam*(H0/100)**2 - ombh2 - {OMNUH2}",
                      "derived": True},
            "omk": 0.0,
            "tau": 0.055, "ns": 0.965, "logA": 3.05,
            "As": {"value": "lambda logA: 1e-10*np.exp(logA)", "derived": True},
        },
        "stop_at_error": True,
    }
    model = get_model(info)
    logp = model.loglikes({}, return_derived=False)[0]
    cob_chi2 = -2.0 * float(np.sum(logp))
    our_chi2, our_rd = ours(**REF)
    print(f"  cobaya  chi2 = {cob_chi2:.6f}")
    print(f"  ours    chi2 = {our_chi2:.6f}")
    print(f"  difference   = {cob_chi2 - our_chi2:+.2e}")
    print(f"  our r_drag   = {our_rd:.5f} Mpc")

    print("\n== 2. r_drag against CAMB settings ==")
    base = None
    for label, kw in [
        ("default (what the fit used)", {}),
        ("AccuracyBoost=2", {"AccuracyBoost": 2.0}),
        ("AccuracyBoost=3", {"AccuracyBoost": 3.0}),
        ("recombination CosmoRec", {"recombination_model": "CosmoRec"}),
        ("recombination HyRec", {"recombination_model": "HyRec"}),
    ]:
        try:
            c2, rd = ours(**REF, **kw)
            if base is None:
                base = rd
            dh0 = REF["H0"] * (base / rd - 1)
            print(f"  {label:30s} r_drag = {rd:9.5f} Mpc  "
                  f"({100*(rd/base-1):+.4f}%)  would move H0 by {dh0:+.4f}")
        except Exception as exc:
            print(f"  {label:30s} not available: {type(exc).__name__}: "
                  f"{str(exc)[:80]}")


if __name__ == "__main__":
    main()
