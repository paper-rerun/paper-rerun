"""Name the HMM states anatomically, so the paper's "sensorimotor network (state 4)"
style claims can be checked without relying on state index.

For each state we take the raw 38-parcel time series, trimmed exactly as the prepared
data was, keep the time points the Viterbi path assigns to that state, and compute a
Welch PSD per parcel. Band power relative to the across-state mean then says which
parcels and which frequencies each state lives in.

Usage: python identify_networks.py runs/run01
"""

import os
import sys

os.environ["CUDA_VISIBLE_DEVICES"] = ""
os.environ["PYTHONIOENCODING"] = "utf-8"

import pickle
import numpy as np
from scipy.signal import welch

from osl_dynamics.data import Data
from osl_dynamics.inference import modes

D = sys.argv[1]
ROOT = r"E:\Ciencia\noturno\2024-gohil-osl-dynamics"
FS = 250

data = Data(
    os.path.join(ROOT, "training_data", "networks"),
    sampling_frequency=FS,
    n_jobs=4,
    store_dir=os.path.join(D, "tmp_ident"),
)
raw = data.trim_time_series(n_embeddings=15, sequence_length=200, prepared=False)

alp = pickle.load(open(f"{D}/alp.pkl", "rb"))
stc = modes.argmax_time_courses(alp)
n_states = stc[0].shape[-1]
print("n_states", n_states, "lengths", raw[0].shape, stc[0].shape, flush=True)

cent = np.load(r"E:\Ciencia\noturno\2024-gohil-osl-dynamics-cego\parcel_centroids.npy")

# Accumulate PSDs over subjects
psd_sum = None
for x, s in zip(raw, stc):
    n = min(len(x), len(s))
    x, s = x[:n], s[:n]
    for k in range(n_states):
        m = s[:, k].astype(bool)
        if m.sum() < FS:
            continue
        f, pxx = welch(x[m].T, fs=FS, nperseg=250)
        if psd_sum is None:
            psd_sum = np.zeros((n_states, x.shape[1], len(f)))
            cnt = np.zeros(n_states)
        psd_sum[k] += pxx
        cnt[k] += 1
f_ax = f
psd = psd_sum / cnt[:, None, None]
np.save(f"{D}/state_psd.npy", psd)
np.save(f"{D}/state_psd_freqs.npy", f_ax)

bands = {"delta": (1, 4), "theta": (4, 8), "alpha": (8, 13), "beta": (13, 30)}
rel = psd - psd.mean(axis=0, keepdims=True)  # relative to the mean across states

# Regions of interest from the MNI centroids of the Giles 38-parcel atlas
roi = {
    "sensorimotor": [8, 9, 18, 19, 4, 5],       # pre/postcentral, paracentral
    "visual": [0, 1, 24, 25, 2, 3],             # occipital
    "dmn_midline": [36, 37, 28, 29],            # precuneus/PCC, mPFC
    "left_temporal": [6, 16, 32, 20],           # left superior/middle temporal
}

print("\nParcel centroids used per ROI:")
for k, v in roi.items():
    print(f"  {k}: {[list(np.round(cent[i], 0).astype(int)) for i in v]}")

print("\nRelative band power (state minus across-state mean), averaged over ROI parcels")
hdr = "state " + " ".join(f"{b:>9s}" for b in bands) + "   " + " ".join(f"{r:>14s}" for r in roi)
print(hdr)
for k in range(n_states):
    row = f"{k + 1:5d} "
    for b, (lo, hi) in bands.items():
        sel = (f_ax >= lo) & (f_ax < hi)
        row += f"{rel[k][:, sel].mean():9.4f} "
    row += "  "
    # beta power in each ROI (and alpha for visual), relative
    for r, idx in roi.items():
        band = (f_ax >= 8) & (f_ax < 13) if r == "visual" else (f_ax >= 13) & (f_ax < 30)
        row += f"{rel[k][idx][:, band].mean():14.4f} "
    print(row)
print("\n(visual column is relative alpha power, the others relative beta power)")

data.delete_dir()
