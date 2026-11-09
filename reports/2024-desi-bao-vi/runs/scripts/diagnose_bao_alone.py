"""The authors' own BAO-alone chain, the one behind C1 and C2. Same question as
for C3: does it reproduce the published numbers, and does our grid land where
it lands?"""
import numpy as np

D = "/mnt/e/Ciencia/noturno/2024-desi-bao-vi/data/official/desi-bao-all"

with open(f"{D}/chain.1.txt") as fh:
    cols = fh.readline().lstrip("#").split()
rows = [np.loadtxt(f"{D}/chain.{i}.txt") for i in (1, 2, 3, 4)]
print("rows per chain:", [len(r) for r in rows])
d = np.vstack([r[int(0.3 * len(r)):] for r in rows])
w = d[:, cols.index("weight")]
print(f"combined {len(d)} rows, weight sum {w.sum():.0f}")


def stat(name):
    x = d[:, cols.index(name)]
    m = np.average(x, weights=w)
    return m, np.sqrt(np.average((x - m) ** 2, weights=w))


print("\n  quantity   their chain          paper        shift   ours (grid)")
om, oms = stat("omegam")
rh, rhs = stat("hrdrag")
print(f"  Omega_m    {om:.5f} +/- {oms:.5f}  0.295 +/- 0.015  "
      f"{(om-0.295)/0.015:+.3f}s  0.29468 +/- 0.01463")
print(f"  r_d h      {rh:.4f} +/- {rhs:.4f}  101.8 +/- 1.3    "
      f"{(rh-101.8)/1.3:+.3f}s  101.8953 +/- 1.2672")

print("\n  our grid against THEIR chain, not against the printed number:")
print(f"  Omega_m  ours - theirs = {0.29468 - om:+.6f}  "
      f"({(0.29468 - om)/0.015:+.3f} published sigma)")
print(f"  r_d h    ours - theirs = {101.8953 - rh:+.5f} Mpc  "
      f"({(101.8953 - rh)/1.3:+.3f} published sigma)")

i = int(np.argmin(d[:, cols.index("minuslogpost")]))
print(f"\n  their best chi2__BAO in the chain: "
      f"{d[i, cols.index('chi2__BAO')]:.4f} at Omega_m="
      f"{d[i, cols.index('omegam')]:.4f}, r_d h="
      f"{d[i, cols.index('hrdrag')]:.3f}")
print(f"  our grid chi2_min: 12.7383")
