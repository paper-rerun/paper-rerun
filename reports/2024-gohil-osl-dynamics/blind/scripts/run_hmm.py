"""Blind reproduction: train an 8-state TDE-HMM on the CTF rest data and run the
young vs old group comparison, following the authors' own
examples/toolbox_paper/ctf_rest/tde_hmm_networks.py config.

Usage: python run_hmm.py <run_id>
"""

import os
import sys

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
from osl_dynamics.models.hmm import Config, Model
from osl_dynamics.inference import modes

RUN = int(sys.argv[1])
ROOT = r"E:\Ciencia\noturno\2024-gohil-osl-dynamics"
OUT = rf"E:\Ciencia\noturno\2024-gohil-osl-dynamics-cego\runs\run{RUN:02d}"
os.makedirs(OUT, exist_ok=True)

# Load and prepare the data exactly as the authors' config does
data = Data(
    os.path.join(ROOT, "training_data", "networks"),
    sampling_frequency=250,
    n_jobs=4,
    store_dir=os.path.join(OUT, "tmp"),
)
data.prepare({"tde_pca": {"n_embeddings": 15, "n_pca_components": 80}, "standardize": {}})
print("n_subjects", data.n_sessions, "n_channels", data.n_channels, flush=True)

# Train the HMM. Seeded per run so the run is reproducible, but note HMM training
# is stochastic across seeds
tf.keras.utils.set_random_seed(RUN)
config = Config(
    n_states=8,
    n_channels=data.n_channels,
    sequence_length=200,
    learn_means=False,
    learn_covariances=True,
    batch_size=256,
    learning_rate=0.01,
    n_epochs=20,
)
model = Model(config)
model.initialization(data, n_init=5, n_epochs=2)
model.fit(data)

free_energy = model.free_energy(data)
print("free_energy", free_energy, flush=True)
np.save(f"{OUT}/free_energy.npy", np.array([free_energy]))
model.save(f"{OUT}/model")

# Inferred state probabilities, then the Viterbi path
alp = model.get_alpha(data)
pickle.dump(alp, open(f"{OUT}/alp.pkl", "wb"))
stc = modes.argmax_time_courses(alp)

fo = modes.fractional_occupancies(stc)
lt = modes.mean_lifetimes(stc, sampling_frequency=250)
intv = modes.mean_intervals(stc, sampling_frequency=250)
sr = modes.switching_rates(stc, sampling_frequency=250)
sum_stats = np.swapaxes([fo, lt, intv, sr], 0, 1)  # (n_subj, 4, n_states)
np.save(f"{OUT}/sum_stats.npy", sum_stats)

# Group assignments, from the authors' rule: age > 34 is old
demographics = pd.read_csv(os.path.join(ROOT, "training_data", "demographics.csv"))
age = demographics["age"].values
assignments = np.ones_like(age)
for i, a in enumerate(age):
    if a > 34:
        assignments[i] += 1
np.save(f"{OUT}/assignments.npy", assignments)

result = stats.group_diff(data=sum_stats, assignments=assignments, n_perm=1000, n_jobs=4)
# Contrast is group1 - group2 = young - old
np.save(f"{OUT}/pvalues.npy", result.pvalues.reshape(4, 8))
np.save(f"{OUT}/copes.npy", result.copes.reshape(4, 8))
print("pvalues\n", result.pvalues.reshape(4, 8), flush=True)
print("copes (young - old)\n", result.copes.reshape(4, 8), flush=True)

data.delete_dir()
print("DONE run", RUN, flush=True)
