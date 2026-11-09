"""Why our DESI+BBN H0 sits above the paper's.

Uses the authors' own published chain for base LCDM, DESI BAO + BBN. Three
questions, each answered from their columns, not from our fit:

  Q1  Does their chain reproduce the published H0 = 68.53 +/- 0.80? If not, we
      are reading the claim wrong and that is the first thing to know.
  Q2  What BBN prior does their chi2__bbn column actually impose? The paper
      quotes omega_b = 0.02218 +/- 0.00055 (Eq. 2.8), but the run used a
      likelihood class called schoneberg2024, not a Gaussian prior, so this is
      worth measuring rather than assuming.
  Q3  Does our CAMB give their r_drag at their own parameter values? This
      separates "our sound horizon is off" from "our posterior is off".
"""
import numpy as np
import camb

OFF = ("/mnt/e/Ciencia/noturno/2024-desi-bao-vi/data/official/"
       "desi-bao-all_schoneberg2024-bbn")

with open(f"{OFF}/chain.1.txt") as fh:
    cols = fh.readline().lstrip("#").split()

rows = [np.loadtxt(f"{OFF}/chain.{i}.txt") for i in (1, 2, 3, 4)]
print("rows per chain:", [len(r) for r in rows])
# Cobaya writes burn-in into the file; drop the first 30% of each chain, which
# is what getdist's default ignore_rows=0.3 would do.
d = np.vstack([r[int(0.3 * len(r)):] for r in rows])
w = d[:, cols.index("weight")]
print(f"combined: {len(d)} rows, weight sum {w.sum():.0f}")


def stat(name):
    x = d[:, cols.index(name)]
    m = np.average(x, weights=w)
    s = np.sqrt(np.average((x - m) ** 2, weights=w))
    return m, s


print("\n-- Q1: their chain against the published numbers --")
for name, pub in (("H0", (68.53, 0.80)), ("omegam", (0.295, 0.015))):
    m, s = stat(name)
    print(f"  {name:8s} chain {m:.5f} +/- {s:.5f} | paper {pub[0]} +/- {pub[1]}"
          f" | shift {(m - pub[0]) / pub[1]:+.3f} sigma")
m, s = stat("H0rdrag")
print(f"  r_d h    chain {m/100:.5f} +/- {s/100:.5f} Mpc  "
      f"(H0*rdrag/100; this run has BBN, so not the BAO-alone 101.8)")

print("\n-- Q2: the BBN term they actually used --")
ob = d[:, cols.index("ombh2")]
chi2b = d[:, cols.index("chi2__bbn")]
# If the term is Gaussian, chi2 = ((ob-mu)/sig)^2 + c. Fit a parabola in ob.
c2, c1, c0 = np.polyfit(ob, chi2b, 2, w=w)
mu = -c1 / (2 * c2)
sig = 1.0 / np.sqrt(c2)
resid = chi2b - np.polyval([c2, c1, c0], ob)
print(f"  parabola fit to chi2__bbn(omega_b): mean {mu:.6f}, sigma {sig:.6f}")
print(f"  paper Eq. (2.8):                    mean 0.022180, sigma 0.000550")
print(f"  residual of the parabola fit: rms {np.sqrt(np.average(resid**2, weights=w)):.3e}"
      f", max |.| {np.abs(resid).max():.3e}  (small rms means it is Gaussian)")
m, s = stat("ombh2")
print(f"  their omega_b marginal: {m:.6f} +/- {s:.6f}")
print(f"  ours (grid):             0.022186 +/- 0.000550")

print("\n-- Q3: our CAMB r_drag at their own parameter values --")
rng = np.random.default_rng(8112026)
pick = rng.choice(len(d), size=200, replace=False)
ours, theirs = [], []
for i in pick:
    H0 = d[i, cols.index("H0")]
    obh2 = d[i, cols.index("ombh2")]
    och2 = d[i, cols.index("omch2")]
    pars = camb.set_params(H0=H0, ombh2=obh2, omch2=och2, mnu=0.06, nnu=3.044,
                           omk=0.0, TCMB=2.7255, num_massive_neutrinos=1)
    ours.append(camb.get_background(pars).get_derived_params()["rdrag"])
    theirs.append(d[i, cols.index("rdrag")])
ours = np.array(ours); theirs = np.array(theirs)
rel = ours / theirs - 1
print(f"  200 samples: our r_drag / their r_drag - 1 = "
      f"{rel.mean():+.3e} +/- {rel.std():.1e}  "
      f"(min {rel.min():+.2e}, max {rel.max():+.2e})")
print(f"  that would move H0 by {-rel.mean() * 68.53:+.4f} km/s/Mpc")
print(f"  their r_drag range in these samples: "
      f"{theirs.min():.3f} .. {theirs.max():.3f} Mpc")

print("\n-- Q4: does their likelihood give our chi2? --")
print(f"  their chi2__BAO at the posterior maximum of the chain: "
      f"{d[np.argmin(d[:, cols.index('minuslogpost')]), cols.index('chi2__BAO')]:.4f}")
print(f"  our grid chi2_min (BAO term only, BAO+BBN fit): see runs/out/results.json")
