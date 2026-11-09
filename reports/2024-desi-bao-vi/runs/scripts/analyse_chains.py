"""Our own cobaya Metropolis-Hastings run for DESI BAO + BBN, read straight
from the four chain files. This is an independent check on our grid: same
likelihood, same priors, a real sampler instead of a grid.

Reads whatever rows are on disk, so it does not depend on cobaya's stopping
rule having fired. Reports the Gelman-Rubin R-1 across the four chains and the
effective sample size, so the reader can judge whether it had converged.
"""
import numpy as np

CH = "/mnt/e/Ciencia/noturno/2024-desi-bao-vi/runs/chains"
BURN = 0.3


def read(i):
    with open(f"{CH}/c{i}.1.txt") as fh:
        cols = fh.readline().lstrip("#").split()
    a = np.loadtxt(f"{CH}/c{i}.1.txt")
    return cols, a[int(BURN * len(a)):]


cols, _ = read(1)
print("columns:", " ".join(cols))
parts = [read(i)[1] for i in (1, 2, 3, 4)]
print("post-burn-in rows:", [len(p) for p in parts])


def wstat(a, j):
    w = a[:, cols.index("weight")]
    x = a[:, j]
    m = np.average(x, weights=w)
    return m, np.sqrt(np.average((x - m) ** 2, weights=w)), w.sum()


def ess(a, j):
    """Effective sample size from the autocorrelation of the weighted chain,
    expanded to unit weights."""
    w = a[:, cols.index("weight")].astype(int)
    x = np.repeat(a[:, j], w)
    x = x - x.mean()
    n = len(x)
    f = np.fft.rfft(x, 2 * n)
    ac = np.fft.irfft(f * np.conj(f))[:n].real
    ac /= ac[0]
    # Geyer initial positive sequence.
    s, k = 0.0, 1
    while k < n - 1 and ac[k] + ac[k + 1] > 0:
        s += ac[k] + ac[k + 1]
        k += 2
    return n / (1 + 2 * s)


print("\n-- marginals of our MCMC, per parameter --")
for name in ("H0", "omegam", "ombh2", "rdrag", "rdh"):
    if name not in cols:
        continue
    j = cols.index(name)
    # Combined.
    allrows = np.vstack(parts)
    m, s, wsum = wstat(allrows, j)
    # Gelman-Rubin across the four chains.
    means = np.array([wstat(p, j)[0] for p in parts])
    varis = np.array([wstat(p, j)[1] ** 2 for p in parts])
    B, W = means.var(ddof=1), varis.mean()
    r1 = B / W
    e = sum(ess(p, j) for p in parts)
    print(f"  {name:8s} {m:12.6f} +/- {s:.6f}   R-1 {r1:.5f}   ESS {e:.0f}")

print(f"\n  combined weight sum: {np.vstack(parts)[:, cols.index('weight')].sum():.0f}")
print("\n-- our MCMC against our grid and against the paper --")
j = cols.index("H0")
m, s, _ = wstat(np.vstack(parts), j)
print(f"  H0  MCMC {m:.4f} +/- {s:.4f}")
print(f"      grid 68.6912 +/- 0.8127   (MCMC - grid = {m - 68.6912:+.4f})")
print(f"      paper 68.53 +/- 0.80      (MCMC - paper = {m - 68.53:+.4f} = "
      f"{(m - 68.53)/0.80:+.3f} sigma)")
j = cols.index("omegam")
m, s, _ = wstat(np.vstack(parts), j)
print(f"  Omega_m MCMC {m:.5f} +/- {s:.5f}   grid 0.29519 +/- 0.01467")
