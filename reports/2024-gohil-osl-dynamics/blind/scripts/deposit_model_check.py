"""Independent control: use the authors' OWN deposited HMM weights
(downloads/trained_tde_hmm.zip, a 12-state model) on all 65 subjects, and ask which
way its sensorimotor-beta state moves with age. If my retrained 8-state models and the
authors' deposited model agree on the direction, the direction is not an artefact of
my training.
"""

import os

os.environ["CUDA_VISIBLE_DEVICES"] = ""
os.environ["PYTHONIOENCODING"] = "utf-8"

import psutil

psutil.Process().nice(psutil.IDLE_PRIORITY_CLASS)

import pickle
import numpy as np
import pandas as pd
import tensorflow as tf

tf.config.set_visible_devices([], "GPU")

from osl_dynamics import stats
from osl_dynamics.data import Data
from osl_dynamics.models import hmm
from osl_dynamics.inference import modes
from scipy.signal import welch
from scipy.stats import pearsonr

ROOT = r"E:\Ciencia\noturno\2024-gohil-osl-dynamics"
HERE = r"E:\Ciencia\noturno\2024-gohil-osl-dynamics-cego"
OUT = os.path.join(HERE, "runs", "deposit12")
os.makedirs(OUT, exist_ok=True)

data = Data(
    os.path.join(ROOT, "training_data", "networks"),
    sampling_frequency=250,
    n_jobs=4,
    store_dir=os.path.join(OUT, "tmp"),
)
data.prepare({"tde_pca": {"n_embeddings": 15, "n_pca_components": 80}, "standardize": {}})

# Does my PCA match the one the authors deposited with the DyNeMo runs?
mine = data.pca_components
theirs = np.load(os.path.join(HERE, "deposit", "tde_dynemo_20_runs", "pca_components.npy"))
cos = np.abs(np.sum(mine * theirs, axis=0)) / (
    np.linalg.norm(mine, axis=0) * np.linalg.norm(theirs, axis=0)
)
print("PCA component agreement with the deposited pca_components.npy:", flush=True)
print("  shapes", mine.shape, theirs.shape)
print("  |cosine| per component: min %.4f  median %.4f" % (cos.min(), np.median(cos)), flush=True)

model = hmm.Model.load(os.path.join(HERE, "deposit", "trained_tde_hmm"))
print("loaded deposited model, n_states", model.config.n_states, flush=True)

alp = model.get_alpha(data)
pickle.dump(alp, open(f"{OUT}/alp.pkl", "wb"))
stc = modes.argmax_time_courses(alp)
n_states = stc[0].shape[-1]

fo = modes.fractional_occupancies(stc)
lt = modes.mean_lifetimes(stc, sampling_frequency=250)
intv = modes.mean_intervals(stc, sampling_frequency=250)
sr = modes.switching_rates(stc, sampling_frequency=250)
sum_stats = np.swapaxes([fo, lt, intv, sr], 0, 1)
np.save(f"{OUT}/sum_stats.npy", sum_stats)

demographics = pd.read_csv(os.path.join(ROOT, "training_data", "demographics.csv"))
age = demographics["age"].values
assignments = np.ones_like(age)
for i, a in enumerate(age):
    if a > 34:
        assignments[i] += 1
np.save(f"{OUT}/assignments.npy", assignments)
np.save(f"{OUT}/free_energy.npy", np.array([np.nan]))

res = stats.group_diff(data=sum_stats, assignments=assignments, n_perm=1000, n_jobs=4)
p = res.pvalues.reshape(4, n_states)
np.save(f"{OUT}/pvalues.npy", p)
np.save(f"{OUT}/copes.npy", res.copes.reshape(4, n_states))

# Label the states from the data, same way as identify_networks.py
raw = data.trim_time_series(n_embeddings=15, sequence_length=200, prepared=False)
psd_sum = None
cnt = np.zeros(n_states)
for x, s in zip(raw, stc):
    n = min(len(x), len(s))
    x, s = x[:n], s[:n]
    for k in range(n_states):
        m = s[:, k].astype(bool)
        if m.sum() < 250:
            continue
        f, pxx = welch(x[m].T, fs=250, nperseg=250)
        if psd_sum is None:
            psd_sum = np.zeros((n_states, x.shape[1], len(f)))
        psd_sum[k] += pxx
        cnt[k] += 1
psd = psd_sum / cnt[:, None, None]
np.save(f"{OUT}/state_psd.npy", psd)
np.save(f"{OUT}/state_psd_freqs.npy", f)

rel = psd - psd.mean(0, keepdims=True)
SM = [8, 9, 18, 19, 4, 5]
VIS = [0, 1, 24, 25, 2, 3]
b = (f >= 13) & (f < 30)
a_ = (f >= 8) & (f < 13)
METRICS = ["FracOcc", "MeanLifetime", "MeanInterval", "SwitchRate"]
young, old = assignments == 1, assignments == 2

print("\nstate | SM beta excess | VIS alpha excess | peak | FO young | FO old | r(FO,age) | p_FO")
smx_all = []
for k in range(n_states):
    smx = rel[k][SM][:, b].mean() - rel[k][:, b].mean()
    vx = rel[k][VIS][:, a_].mean() - rel[k][:, a_].mean()
    sel = (f >= 2) & (f < 40)
    pk = f[sel][np.argmax(rel[k][:, sel].mean(0))]
    r, pr = pearsonr(age, fo[:, k])
    smx_all.append(smx)
    print(
        f"{k + 1:5d} | {smx:14.4f} | {vx:16.4f} | {pk:4.0f}Hz |"
        f" {fo[young, k].mean():8.4f} | {fo[old, k].mean():6.4f} | {r:+9.3f} | {pr:.4g}"
    )

best = int(np.argmax(smx_all))
print(f"\nMost sensorimotor-specific state in the DEPOSITED model: state {best + 1}")
print(f"  FO  young {fo[young, best].mean():.5f}  old {fo[old, best].mean():.5f}  "
      f"p(max-stat)={p[0, best]:.4f}")
print(f"  SR  young {sr[young, best].mean():.5f}  old {sr[old, best].mean():.5f}  "
      f"p(max-stat)={p[3, best]:.4f}")
print("\nAll significant effects, p<0.05 max-stat:")
for i, s in np.argwhere(p < 0.05):
    y, o = sum_stats[young, i, s].mean(), sum_stats[old, i, s].mean()
    print(f"  {METRICS[i]:13s} state {s + 1}  p={p[i, s]:.4f}  "
          f"{'INCREASED' if o > y else 'DECREASED'} in old  young={y:.5f} old={o:.5f}")

data.delete_dir()
print("DONE deposit check", flush=True)
