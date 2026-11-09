"""The sibling chain: schoneberg2024_fixed_nnu. Which omega_b constraint does
it impose, and what H0 does it give?"""
import numpy as np

D = ("/mnt/e/Ciencia/noturno/2024-desi-bao-vi/data/official/"
     "sibling-fixed-nnu")

with open(f"{D}/chain.1.txt") as fh:
    cols = fh.readline().lstrip("#").split()
rows = [np.loadtxt(f"{D}/chain.{i}.txt") for i in (1, 2)]
d = np.vstack([r[int(0.3 * len(r)):] for r in rows])
w = d[:, cols.index("weight")]
print(f"2 of 4 chains, {len(d)} rows, weight sum {w.sum():.0f}")

bbn_col = [c for c in cols if c.startswith("chi2__") and "bbn" in c.lower()]
print("bbn chi2 columns:", bbn_col)


def stat(name):
    x = d[:, cols.index(name)]
    m = np.average(x, weights=w)
    return m, np.sqrt(np.average((x - m) ** 2, weights=w))


for n in ("H0", "omegam", "ombh2"):
    m, s = stat(n)
    print(f"  {n:8s} {m:.6f} +/- {s:.6f}")

ob = d[:, cols.index("ombh2")]
chi2b = d[:, cols.index("chi2__bbn")]
c2, c1, c0 = np.polyfit(ob, chi2b, 2, w=w)
print(f"\n  parabola fit to chi2__bbn: mean {-c1/(2*c2):.6f}, "
      f"sigma {1/np.sqrt(c2):.6f}")
print(f"  paper Eq. (2.8) for LCDM:  mean 0.022180, sigma 0.000550")
print(f"  paper Eq. (2.9) for +Neff: mean 0.021960, sigma 0.000630")
