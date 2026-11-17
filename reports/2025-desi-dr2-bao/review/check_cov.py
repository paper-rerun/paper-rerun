"""Independent re-derivation of the report's covariance finding.

Reads only data/, writes nothing. Two questions:
  1. Do the file sigmas and correlations match what cov_vs_table.log printed?
  2. Which set - Table IV's own (DM, DH, r_MH) or the released covariance's -
     reproduces the DV/rd and DM/DH uncertainties ALSO printed in Table IV?
     That tells us which of the two is the odd one out, independently of any
     story about marginalised posteriors.
"""
import numpy as np

DATA = "/mnt/e/Ciencia/noturno/2025-desi-dr2-bao/data"

# Table IV, read off the paper text (lines 852-868 of paper.txt)
# z: (DM, sDM, DH, sDH, r_MH, DV, sDV, FAP, sFAP, r_V_MH)
T4 = {
    0.510: (13.588, 0.167, 21.863, 0.425, -0.459, 12.720, 0.099, 0.622, 0.017, 0.050),
    0.706: (17.351, 0.177, 19.455, 0.330, -0.404, 16.050, 0.110, 0.892, 0.021, -0.018),
    0.934: (21.576, 0.152, 17.641, 0.193, -0.416, 19.721, 0.091, 1.223, 0.019, 0.056),
    1.321: (27.601, 0.318, 14.176, 0.221, -0.434, 24.252, 0.174, 1.948, 0.045, 0.202),
    1.484: (30.512, 0.760, 12.817, 0.516, -0.500, 26.055, 0.398, 2.386, 0.136, 0.044),
    2.330: (38.988, 0.531, 8.632, 0.101, -0.431, 31.267, 0.256, 4.518, 0.097, 0.574),
}
NAME = {0.295: "BGS", 0.510: "LRG1", 0.706: "LRG2", 0.934: "LRG3+ELG1",
        1.321: "ELG2", 1.484: "QSO", 2.330: "Lya"}


def propagate(dm, sdm, dh, sdh, r):
    """sigma of DV and of F_AP = DM/DH from (DM, DH) and their correlation."""
    vm, vh = (sdm / dm) ** 2, (sdh / dh) ** 2
    cmh = r * (sdm / dm) * (sdh / dh)
    dv = (dm ** 2 * dh) ** (1.0 / 3.0)          # z factor cancels in the ratio
    rel_dv = np.sqrt(4 / 9 * vm + 1 / 9 * vh + 4 / 9 * cmh)
    fap = dm / dh
    rel_fap = np.sqrt(vm + vh - 2 * cmh)
    # correlation between DV and F_AP
    cov_lv_lf = 2 / 3 * vm + 1 / 3 * cmh - 2 / 3 * cmh - 1 / 3 * vh
    r_vf = cov_lv_lf / (rel_dv * rel_fap)
    return dv, rel_dv * dv, fap, rel_fap * fap, r_vf


z, kind = [], []
with open(f"{DATA}/desi_dr2_gaussian_bao_ALL_GCcomb_mean.txt") as fh:
    for line in fh:
        if line.startswith("#") or not line.strip():
            continue
        a, _, c = line.split()
        z.append(float(a)); kind.append(c)
z = np.array(z)
cov = np.loadtxt(f"{DATA}/desi_dr2_gaussian_bao_ALL_GCcomb_cov.txt")
sig = np.sqrt(np.diag(cov))

print("== 1. file sigma / correlation, recomputed independently ==")
for zz in sorted(set(z)):
    idx = [i for i in range(len(z)) if z[i] == zz]
    for i in idx:
        print(f"  {NAME[zz]:<10s} z={zz:.3f} {kind[i]:<11s} sigma_file={sig[i]:.6f}")
    if len(idx) == 2:
        a, b = idx
        print(f"  {NAME[zz]:<10s} corr_file={cov[a, b] / (sig[a] * sig[b]):+.6f} "
              f"(table {T4[zz][4]:+.3f})")

print("\n== 2. internal consistency of Table IV with itself vs with the file ==")
print(f"{'tracer':<10s} {'src':<6s} {'sDV':>8s} {'T4 sDV':>8s} {'ratio':>7s} "
      f"{'sFAP':>8s} {'T4 sFAP':>8s} {'ratio':>7s} {'r_V,MH':>8s} {'T4 r':>6s}")
for zz in sorted(T4):
    dm_t, sdm_t, dh_t, sdh_t, r_t, dv_t, sdv_t, fap_t, sfap_t, rv_t = T4[zz]
    idx = {kind[i]: i for i in range(len(z)) if z[i] == zz}
    im, ih = idx["DM_over_rs"], idx["DH_over_rs"]
    rf = cov[im, ih] / (sig[im] * sig[ih])
    for src, (dm, sdm, dh, sdh, r) in (
            ("table", (dm_t, sdm_t, dh_t, sdh_t, r_t)),
            ("file", (dm_t, sig[im], dh_t, sig[ih], rf))):
        dv, sdv, fap, sfap, rvf = propagate(dm, sdm, dh, sdh, r)
        # DV in the table includes the z factor; compare relative sigmas only
        rel = sdv / dv
        print(f"{NAME[zz]:<10s} {src:<6s} {rel * dv_t:8.4f} {sdv_t:8.3f} "
              f"{rel * dv_t / sdv_t:7.4f} {sfap:8.4f} {sfap_t:8.3f} "
              f"{sfap / sfap_t:7.4f} {rvf:+8.4f} {rv_t:+6.3f}")
