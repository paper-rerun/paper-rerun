"""Confirmation of the diagnosis: rerun the BAO+BBN grid with the omega_b
constraint the authors' chain actually imposed, instead of the one printed in
the paper. Everything else is the frozen pre-registered setup.

This is an ALTERNATIVE READING reported alongside the pre-registered result.
It does not replace it and does not change the verdict on C3.
"""
import json
import sys
import numpy as np
from scipy.interpolate import RectBivariateSpline

sys.path.insert(0, "/mnt/e/Ciencia/noturno/2024-desi-bao-vi/runs/scripts")
import fit as F   # reuses the frozen grids and likelihood, unchanged

OUT = F.OUT

VARIANTS = {
    "paper_eq_2_8 (pre-registered)": (0.02218, 0.00055),
    "authors_chain_measured": (0.021976, 0.000534),
    "paper_eq_2_9 (LCDM+Neff value)": (0.02196, 0.00063),
}


def main():
    hs = F.H0_D / 100.0
    d = F.stage_a("d", F.OM_D, hs, 6)             # cached from the main run
    dm_all, dh_all = d["dm_h"], d["dh_h"]
    tab = F.stage_b(6)                            # cached
    spline = RectBivariateSpline(tab["ob"], tab["om2"], tab["rd"], kx=3, ky=3)

    om2 = F.OM_D[None, :, None] * (hs ** 2)[:, None, None]
    om2 = np.broadcast_to(om2, (len(F.H0_D), len(F.OM_D), len(F.OB_D)))
    obg = np.broadcast_to(F.OB_D[None, None, :], om2.shape)
    rdh = spline.ev(obg, om2) * hs[:, None, None]

    dm = np.broadcast_to(dm_all[:, :, None, :],
                         (len(F.H0_D), len(F.OM_D), len(F.OB_D), len(F.ZU)))
    dh = np.broadcast_to(dh_all[:, :, None, :], dm.shape)
    c2_bao = F.chi2_grid(dm, dh, rdh)

    out = {}
    for label, (mu, sig) in VARIANTS.items():
        c2 = c2_bao + ((F.OB_D - mu) / sig) ** 2
        got = F.marg(-0.5 * c2, {"H0": F.H0_D, "Omega_m": F.OM_D,
                                 "omega_b": F.OB_D},
                     ["H0", "Omega_m", "omega_b"])
        h0m, h0s, h0e = got["H0"]
        print(f"{label:34s} omega_b prior {mu:.6f} +/- {sig:.6f}")
        print(f"{'':34s} -> H0 = {h0m:.4f} +/- {h0s:.4f}  "
              f"(paper 68.53 +/- 0.80, shift {(h0m-68.53)/0.80:+.3f} sigma, "
              f"edge mass {h0e:.1e})")
        print(f"{'':34s}    Omega_m = {got['Omega_m'][0]:.5f} +/- "
              f"{got['Omega_m'][1]:.5f}, omega_b marginal = "
              f"{got['omega_b'][0]:.6f} +/- {got['omega_b'][1]:.6f}")
        out[label] = {"omega_b_prior": [mu, sig],
                      "H0_mean": h0m, "H0_sigma": h0s,
                      "H0_shift_sigma": (h0m - 68.53) / 0.80,
                      "Omega_m_mean": got["Omega_m"][0],
                      "Omega_m_sigma": got["Omega_m"][1]}
    with open(f"{OUT}/variant_bbn.json", "w") as fh:
        json.dump(out, fh, indent=2, default=float)
    print(f"\nwritten {OUT}/variant_bbn.json")


if __name__ == "__main__":
    main()
