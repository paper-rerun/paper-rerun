"""One table per run: free energy, anatomical label per state, and every significant
group effect with its direction. Usage: python summarize.py runs/run01 runs/run02 ...
"""

import os
import sys

os.environ["PYTHONIOENCODING"] = "utf-8"
import numpy as np

METRICS = ["FracOcc", "MeanLifetime", "MeanInterval", "SwitchRate"]
ROI = {
    "sensorimotor": [8, 9, 18, 19, 4, 5],
    "visual": [0, 1, 24, 25, 2, 3],
    "dmn": [36, 37, 28, 29],
    "ltemp": [6, 16, 32, 20],
}


def label_states(d):
    psd = np.load(f"{d}/state_psd.npy")
    f = np.load(f"{d}/state_psd_freqs.npy")
    rel = psd - psd.mean(0, keepdims=True)
    b = (f >= 13) & (f < 30)
    a = (f >= 8) & (f < 13)
    tot = rel[:, :, (f >= 1) & (f < 45)].mean(axis=(1, 2))
    out = []
    for k in range(psd.shape[0]):
        ex = {
            "sensorimotor": rel[k][ROI["sensorimotor"]][:, b].mean() - rel[k][:, b].mean(),
            "visual": rel[k][ROI["visual"]][:, a].mean() - rel[k][:, a].mean(),
            "dmn": rel[k][ROI["dmn"]][:, a].mean() - rel[k][:, a].mean(),
            "ltemp": rel[k][ROI["ltemp"]][:, b].mean() - rel[k][:, b].mean(),
        }
        best = max(ex, key=ex.get)
        sel = (f >= 2) & (f < 40)
        pk = f[sel][np.argmax(rel[k][:, sel].mean(0))]
        tag = f"{best}(+{ex[best]:.3f}) pk{pk:.0f}Hz pow{tot[k]:+.3f}"
        if tot[k] == tot.min():
            tag += " [LOWEST POWER = suppressed]"
        if tot[k] == tot.max():
            tag += " [HIGHEST POWER]"
        out.append(tag)
    return out


for d in sys.argv[1:]:
    if not os.path.exists(f"{d}/pvalues.npy"):
        print(f"{d}: no results")
        continue
    p = np.load(f"{d}/pvalues.npy")
    ss = np.load(f"{d}/sum_stats.npy")
    a = np.load(f"{d}/assignments.npy")
    fe = np.load(f"{d}/free_energy.npy")[0]
    young, old = a == 1, a == 2
    print("=" * 78)
    print(f"{d}   free energy {fe:.4f}")
    if os.path.exists(f"{d}/state_psd.npy"):
        for i, t in enumerate(label_states(d)):
            print(f"  state {i + 1}: {t}")
    print("  significant group effects, p<0.05 max-stat over states x metrics:")
    for i, s in np.argwhere(p < 0.05):
        y, o = ss[young, i, s].mean(), ss[old, i, s].mean()
        sdr = ss[old, i, s].std(ddof=1) / ss[young, i, s].std(ddof=1)
        d_ = "INCREASED in old" if o > y else "DECREASED in old"
        print(
            f"    {METRICS[i]:13s} state {s + 1}  p={p[i, s]:.4f}  {d_}"
            f"  young={y:.5f} old={o:.5f}  sd_old/sd_young={sdr:.3f}"
        )
    print(f"  smallest p: {p.min():.4f}")
    print("  mean lifetime per state (s):", np.round(ss[:, 1, :].mean(0), 4))
    n_in = ((ss[:, 1, :].mean(0) >= 0.050) & (ss[:, 1, :].mean(0) <= 0.100)).sum()
    print(f"  states with mean lifetime in [50,100] ms: {n_in}/{ss.shape[-1]}")
