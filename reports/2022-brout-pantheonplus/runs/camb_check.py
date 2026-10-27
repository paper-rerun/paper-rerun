"""D-BACKGROUND check for P1: CAMB background with the chain values.ini settings instead of the analytic E(z).
Done by importance reweighting the analytic-background posterior of a finished run:
w_camb = w * exp(-(chi2_camb - chi2_analytic) / 2). Usage: python camb_check.py flcdm_dynesty_s1
"""
import json
import os
import sys
import time
import numpy as np
import camb
import pp_like
from run_fit import weighted_stats, OUT

OMEGA_B = 0.048
OMNUH2 = 0.00083


def camb_params(om, h):
    ombh2 = OMEGA_B * h * h
    # Find mnu giving omnuh2 = 0.00083 with 3 degenerate massive species and N_eff 3.046
    mnu = OMNUH2 * 93.14
    for _ in range(5):
        p = camb.CAMBparams()
        p.set_cosmology(H0=100.0 * h, ombh2=ombh2, omch2=0.1, mnu=mnu, nnu=3.046, num_massive_neutrinos=3,
                        neutrino_hierarchy="degenerate", omk=0.0, tau=0.0697186)
        mnu *= OMNUH2 / p.omnuh2
    omch2 = om * h * h - ombh2 - p.omnuh2
    p.set_cosmology(H0=100.0 * h, ombh2=ombh2, omch2=omch2, mnu=mnu, nnu=3.046, num_massive_neutrinos=3,
                    neutrino_hierarchy="degenerate", omk=0.0, tau=0.0697186)
    p.InitPower.set_params(As=2.19e-9, ns=0.97)
    return p


def camb_theory(like, M, om, h):
    res = camb.get_background(camb_params(om, h))
    d_a = res.angular_diameter_distance(like.zHD)
    return 5.0 * np.log10((1.0 + like.zHD) * (1.0 + like.zHEL) * d_a) + 25.0 + M


def main(run):
    like = pp_like.PantheonPlus()
    d = np.load(os.path.join(OUT, run + ".npz"))
    names = list(d["names"])
    s, w = d["samples"], d["weights"] / d["weights"].sum()
    iom, ih, im = names.index("Om"), names.index("h0"), names.index("M")
    # Background difference at the paper's best value
    mu_a = like.mu_cosmo(0.334, 0.7)
    mu_c = camb_theory(like, 0.0, 0.334, 0.7)
    info = dict(run=run, camb_version=camb.__version__,
                max_abs_dmu_mag_at_Om0334_h07=float(np.max(np.abs(mu_c - mu_a))),
                dmu_at_lowest_and_highest_z=[float((mu_c - mu_a)[np.argmin(like.zHD)]),
                                             float((mu_c - mu_a)[np.argmax(like.zHD)])])
    keep = np.where(w > 1e-6 * w.max())[0]
    t0 = time.time()
    dchi2 = np.zeros(len(keep))
    for k, i in enumerate(keep):
        M, om, h = s[i, im], s[i, iom], s[i, ih]
        r_c = like.m_obs - camb_theory(like, M, om, h)
        dchi2[k] = float(r_c @ (like.icov @ r_c)) - like.chi2(M, om, h)
    w_new = w[keep] * np.exp(-0.5 * (dchi2 - dchi2.min()))
    info.update(n_reweighted=int(len(keep)), weight_kept=float(w[keep].sum()), seconds=time.time() - t0,
                dchi2_mean=float(np.average(dchi2, weights=w[keep])), dchi2_std=float(np.std(dchi2)),
                ess_after=float(w_new.sum() ** 2 / np.sum(w_new ** 2)),
                Om_analytic=weighted_stats(s[keep, iom], w[keep]),
                Om_camb=weighted_stats(s[keep, iom], w_new))
    with open(os.path.join(OUT, "camb_check_" + run + ".json"), "w") as f:
        json.dump(info, f, indent=1)
    print(json.dumps({k: v for k, v in info.items() if not k.startswith("Om_")}))
    print("Om analytic %.5f camb %.5f" % (info["Om_analytic"]["mean"], info["Om_camb"]["mean"]))


if __name__ == "__main__":
    main(sys.argv[1])
