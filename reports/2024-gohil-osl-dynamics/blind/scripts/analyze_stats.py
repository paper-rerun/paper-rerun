"""Read a finished run and print the numbers each pre-registered claim needs.

Usage: python analyze_stats.py runs/run01 [runs/run02 ...]
"""

import os
import sys

os.environ["PYTHONIOENCODING"] = "utf-8"
import numpy as np

METRICS = ["Fractional Occupancy", "Mean Lifetime (s)", "Mean Interval (s)", "Switching Rate (Hz)"]

for d in sys.argv[1:]:
    print("=" * 78)
    print(d)
    ss = np.load(f"{d}/sum_stats.npy")          # (n_subj, 4, n_states)
    p = np.load(f"{d}/pvalues.npy")             # (4, n_states)
    cope = np.load(f"{d}/copes.npy")            # (4, n_states), young - old
    a = np.load(f"{d}/assignments.npy")
    fe = np.load(f"{d}/free_energy.npy")[0]
    young, old = a == 1, a == 2
    print(f"free energy {fe:.4f}   n_young {young.sum()}  n_old {old.sum()}")

    for i, name in enumerate(METRICS):
        print(f"\n-- {name}")
        print("state  young_mean   old_mean   old-young   p(max-stat)  sd_young  sd_old  sd_ratio")
        for s in range(ss.shape[-1]):
            y = ss[young, i, s]
            o = ss[old, i, s]
            # copes are young - old, so old - young is the negative
            print(
                f"{s + 1:5d}  {y.mean():10.5f} {o.mean():10.5f} {-cope[i, s]:+11.5f}"
                f" {p[i, s]:12.4f}  {y.std(ddof=1):8.5f} {o.std(ddof=1):7.5f}"
                f" {o.std(ddof=1) / y.std(ddof=1):8.3f}"
            )

    print("\n-- significant at p<0.05 (max-stat corrected over states x metrics)")
    sig = np.argwhere(p < 0.05)
    if len(sig) == 0:
        print("   none")
    for i, s in sig:
        direction = "increased in old" if -cope[i, s] > 0 else "decreased in old"
        print(f"   {METRICS[i]:22s} state {s + 1}  p={p[i, s]:.4f}  {direction}")
    print("\n   smallest p overall:", p.min())
    print("   mean lifetime across subjects per state (s):",
          np.round(ss[:, 1, :].mean(axis=0), 4))
