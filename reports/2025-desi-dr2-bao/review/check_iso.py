"""Where does the released covariance put its extra variance?

Decompose the released 2x2 (D_M/rd, D_H/rd) block of each tracer into the
isotropic (D_V) and the Alcock-Paczynski (F_AP = D_M/D_H) directions and
compare each with Table IV. If the excess sits only in the isotropic
direction, "Table IV is a marginalised posterior, the file is a Gaussian
approximation" is not the only reading: an extra isotropic error term added
to the released likelihood would look exactly like this.
"""
import numpy as np

DATA = "/mnt/e/Ciencia/noturno/2025-desi-dr2-bao/data"
# z: DM, sDM, DH, sDH, r_MH, DV, sDV, FAP, sFAP  (Table IV of 2503.14738)
T4 = {0.510: (13.588, 0.167, 21.863, 0.425, -0.459, 12.720, 0.099, 0.622, 0.017),
      0.706: (17.351, 0.177, 19.455, 0.330, -0.404, 16.050, 0.110, 0.892, 0.021),
      0.934: (21.576, 0.152, 17.641, 0.193, -0.416, 19.721, 0.091, 1.223, 0.019),
      1.321: (27.601, 0.318, 14.176, 0.221, -0.434, 24.252, 0.174, 1.948, 0.045),
      1.484: (30.512, 0.760, 12.817, 0.516, -0.500, 26.055, 0.398, 2.386, 0.136),
      2.330: (38.988, 0.531, 8.632, 0.101, -0.431, 31.267, 0.256, 4.518, 0.097)}
NAME = {0.295: "BGS", 0.510: "LRG1", 0.706: "LRG2", 0.934: "LRG3+ELG1",
        1.321: "ELG2", 1.484: "QSO", 2.330: "Lya"}

z, kind = [], []
with open(f"{DATA}/desi_dr2_gaussian_bao_ALL_GCcomb_mean.txt") as fh:
    for line in fh:
        if line.startswith("#") or not line.strip():
            continue
        a, _, c = line.split()
        z.append(float(a)); kind.append(c)
z = np.array(z)
cov = np.loadtxt(f"{DATA}/desi_dr2_gaussian_bao_ALL_GCcomb_cov.txt")


def rel_dirs(dm, dh, vdm, vdh, cmh):
    """Relative sigma along ln D_V and ln F_AP from a 2x2 block."""
    rm, rh = vdm / dm ** 2, vdh / dh ** 2
    rc = cmh / (dm * dh)
    v_dv = 4 / 9 * rm + 1 / 9 * rh + 4 / 9 * rc
    v_f = rm + rh - 2 * rc
    return np.sqrt(v_dv), np.sqrt(v_f)


print(f"{'tracer':<10s} {'relsig DV file':>14s} {'table':>8s} {'ratio':>7s} "
      f"{'relsig FAP file':>15s} {'table':>8s} {'ratio':>7s} {'extra iso':>10s}")
for zz in sorted(T4):
    dm, sdm, dh, sdh, r, dv, sdv, fap, sfap = T4[zz]
    idx = {kind[i]: i for i in range(len(z)) if z[i] == zz}
    im, ih = idx["DM_over_rs"], idx["DH_over_rs"]
    f_dv, f_f = rel_dirs(dm, dh, cov[im, im], cov[ih, ih], cov[im, ih])
    t_dv, t_f = rel_dirs(dm, dh, sdm ** 2, sdh ** 2, r * sdm * sdh)
    extra = np.sqrt(max(f_dv ** 2 - t_dv ** 2, 0.0))
    print(f"{NAME[zz]:<10s} {f_dv * 100:13.4f}% {t_dv * 100:7.4f}% "
          f"{f_dv / t_dv:7.4f} {f_f * 100:14.4f}% {t_f * 100:7.4f}% "
          f"{f_f / t_f:7.4f} {extra * 100:9.4f}%")

# BGS has one entry only
i = [k for k in range(len(z)) if z[k] == 0.295][0]
f = np.sqrt(cov[i, i]) / 7.942
t = 0.075 / 7.942
print(f"{'BGS':<10s} {f * 100:13.4f}% {t * 100:7.4f}% {f / t:7.4f} "
      f"{'-':>14s} {'-':>8s} {'-':>7s} "
      f"{np.sqrt(max(f ** 2 - t ** 2, 0)) * 100:9.4f}%")
