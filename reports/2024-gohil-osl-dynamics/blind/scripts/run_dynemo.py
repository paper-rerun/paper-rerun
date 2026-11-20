"""Blind reproduction: train a 7-mode TDE-DyNeMo on the CTF rest data and run the
young vs old comparison on the renormalized mode time course mean and sd, following
examples/toolbox_paper/ctf_rest/tde_dynemo_networks.py.

Usage: python run_dynemo.py <run_id>
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
tf.config.threading.set_intra_op_parallelism_threads(4)
tf.config.threading.set_inter_op_parallelism_threads(2)

from osl_dynamics import stats
from osl_dynamics.data import Data
from osl_dynamics.models.dynemo import Config, Model
from osl_dynamics.inference import modes

RUN = int(sys.argv[1])
ROOT = r"E:\Ciencia\noturno\2024-gohil-osl-dynamics"
OUT = rf"E:\Ciencia\noturno\2024-gohil-osl-dynamics-cego\runs\dynemo{RUN:02d}"
os.makedirs(OUT, exist_ok=True)

data = Data(
    os.path.join(ROOT, "training_data", "networks"),
    sampling_frequency=250,
    n_jobs=4,
    store_dir=os.path.join(OUT, "tmp"),
)
data.prepare({"tde_pca": {"n_embeddings": 15, "n_pca_components": 80}, "standardize": {}})
print("n_subjects", data.n_sessions, "n_channels", data.n_channels, flush=True)

tf.keras.utils.set_random_seed(100 + RUN)
config = Config(
    n_modes=7,
    n_channels=data.n_channels,
    sequence_length=200,
    inference_n_units=64,
    inference_normalization="layer",
    model_n_units=64,
    model_normalization="layer",
    learn_alpha_temperature=True,
    initial_alpha_temperature=1.0,
    learn_means=False,
    learn_covariances=True,
    do_kl_annealing=True,
    kl_annealing_curve="tanh",
    kl_annealing_sharpness=10,
    n_kl_annealing_epochs=20,
    batch_size=128,
    learning_rate=0.01,
    lr_decay=0.1,
    n_epochs=40,
)
model = Model(config)
model.fit(data)
free_energy = model.free_energy(data)
print("free_energy", free_energy, flush=True)
np.save(f"{OUT}/free_energy.npy", np.array([free_energy]))
model.save(f"{OUT}/model")

alpha = model.get_alpha(data)
covs = model.get_covariances()
pickle.dump(alpha, open(f"{OUT}/alp.pkl", "wb"))

# Renormalize the mode time course by the trace of each mode covariance, as the
# toolbox does for DyNeMo summary statistics
norm_alpha = modes.reweight_alphas(alpha, covs)
alp_mean = np.array([np.mean(a, axis=0) for a in norm_alpha])
alp_std = np.array([np.std(a, axis=0) for a in norm_alpha])
sum_stats = np.swapaxes([alp_mean, alp_std], 0, 1)  # (n_subj, 2, n_modes)
np.save(f"{OUT}/sum_stats.npy", sum_stats)

demographics = pd.read_csv(os.path.join(ROOT, "training_data", "demographics.csv"))
age = demographics["age"].values
assignments = np.ones_like(age)
for i, a in enumerate(age):
    if a > 34:
        assignments[i] += 1

result = stats.group_diff(data=sum_stats, assignments=assignments, n_perm=1000, n_jobs=4)
np.save(f"{OUT}/pvalues.npy", result.pvalues.reshape(2, 7))
np.save(f"{OUT}/copes.npy", result.copes.reshape(2, 7))
print("pvalues\n", result.pvalues.reshape(2, 7), flush=True)
print("copes (young - old)\n", result.copes.reshape(2, 7), flush=True)

data.delete_dir()
print("DONE dynemo run", RUN, flush=True)
