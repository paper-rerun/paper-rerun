"""The released covariance against the error bars printed in Table IV.

Found by the blind rerun; this is our own check of it. Three things:
  1. Diagonal sigma of the covariance against the sigma printed in Table IV.
  2. Within-tracer D_M-D_H correlation against the one printed in Table IV.
  3. Whether the combined covariance has any cross-tracer term at all.
"""
import numpy as np

DATA = "/mnt/e/Ciencia/noturno/2025-desi-dr2-bao/data"

# Table IV of arXiv:2503.14738, the printed uncertainty of each entry
TABLE4_SIGMA = {
    (0.295, "DV_over_rs"): 0.075,
    (0.510, "DM_over_rs"): 0.167, (0.510, "DH_over_rs"): 0.425,
    (0.706, "DM_over_rs"): 0.177, (0.706, "DH_over_rs"): 0.330,
    (0.934, "DM_over_rs"): 0.152, (0.934, "DH_over_rs"): 0.193,
    (1.321, "DM_over_rs"): 0.318, (1.321, "DH_over_rs"): 0.221,
    (1.484, "DM_over_rs"): 0.760, (1.484, "DH_over_rs"): 0.516,
    (2.330, "DM_over_rs"): 0.531, (2.330, "DH_over_rs"): 0.101,
}

# Table IV, the printed D_M-D_H correlation of each tracer
TABLE4_CORR = {0.510: -0.459, 0.706: -0.404, 0.934: -0.416,
               1.321: -0.434, 1.484: -0.500, 2.330: -0.431}

TRACER = {0.295: "BGS", 0.510: "LRG1", 0.706: "LRG2", 0.934: "LRG3+ELG1",
          1.321: "ELG2", 1.484: "QSO", 2.330: "Lya"}


def main():
    z, kind = [], []
    with open(f"{DATA}/desi_dr2_gaussian_bao_ALL_GCcomb_mean.txt") as fh:
        for line in fh:
            if line.startswith("#") or not line.strip():
                continue
            a, _, c = line.split()
            z.append(float(a)); kind.append(c)
    z = np.array(z)
    cov = np.loadtxt(f"{DATA}/desi_dr2_gaussian_bao_ALL_GCcomb_cov.txt")
    sigma = np.sqrt(np.diag(cov))

    print("-- 1. diagonal sigma against Table IV --")
    print(f"{'tracer':<11s} {'z':>6s} {'quantity':<11s} {'file':>8s} "
          f"{'table':>7s} {'ratio':>7s}")
    ratios = []
    for i, (zz, kk) in enumerate(zip(z, kind)):
        t = TABLE4_SIGMA[(zz, kk)]
        ratios.append(sigma[i] / t)
        print(f"{TRACER[zz]:<11s} {zz:6.3f} {kk:<11s} {sigma[i]:8.4f} "
              f"{t:7.3f} {sigma[i] / t:7.4f}")
    ratios = np.array(ratios)
    print(f"  every released sigma larger: {bool((ratios > 1).all())}")
    print(f"  range of the ratio: {ratios.min():.4f} to {ratios.max():.4f}")

    print("\n-- 2. within-tracer correlation against Table IV --")
    for zz in sorted(set(z)):
        idx = [i for i in range(len(z)) if z[i] == zz]
        if len(idx) != 2:
            continue
        a, b = idx
        r = cov[a, b] / (sigma[a] * sigma[b])
        t = TABLE4_CORR[zz]
        print(f"{TRACER[zz]:<11s} z={zz:.3f}  file {r:+.4f}  table {t:+.3f}  "
              f"diff {r - t:+.4f}")

    print("\n-- 3. cross-tracer terms --")
    n = len(z)
    same = z[:, None] == z[None, :]
    off = ~np.eye(n, dtype=bool)
    cross = cov[off & ~same]
    within = cov[off & same]
    print(f"  off-diagonal, different tracer: {cross.size} entries, "
          f"all exactly zero: {bool((cross == 0).all())}, "
          f"max abs {np.abs(cross).max():.1e}")
    print(f"  off-diagonal, same tracer: {within.size} entries, "
          f"any zero: {bool((within == 0).any())}")


if __name__ == "__main__":
    main()
