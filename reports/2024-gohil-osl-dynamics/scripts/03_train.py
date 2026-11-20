"""Train one 8-state TDE-HMM, the model behind Figure 4.

The config is copied from examples/toolbox_paper/ctf_rest/tde_hmm_networks.py, minus the
plotting steps, which need a display. We go through run_pipeline so the code path is the
authors' own. Nothing here is our own method: the only thing we add is a seed, because the
paper's own figure supplements show three sets of ten runs and we need to say which run is
which.

Usage: python scripts/03_train.py <seed>
"""

import os
import sys
import json
import time

seed = int(sys.argv[1])

# CPU only. The GPU on this machine belongs to someone else.
os.environ["CUDA_VISIBLE_DEVICES"] = ""
os.environ["TF_CPP_MIN_LOG_LEVEL"] = "2"

import psutil
psutil.Process().nice(psutil.IDLE_PRIORITY_CLASS)

import numpy as np
import tensorflow as tf

tf.config.set_visible_devices([], "GPU")
tf.keras.utils.set_random_seed(seed)

from osl_dynamics import run_pipeline

# Copied from tde_hmm_networks.py. plot_* and compare_groups are left out: the first need a
# display, and the group comparison is script 04, where we can run it with several seeds.
config = """
    load_data:
        inputs: training_data/networks
        kwargs:
            sampling_frequency: 250
            parcellation_file: atlas-Giles_nparc-38_space-MNI_res-8x8x8.nii.gz
            n_jobs: 4
        prepare:
            tde_pca: {n_embeddings: 15, n_pca_components: 80}
            standardize: {}
    train_hmm:
        config_kwargs:
            n_states: 8
            learn_means: False
            learn_covariances: True
"""

output_dir = f"runs/hmm/seed{seed:02d}"
start = time.time()
run_pipeline(config, output_dir=output_dir)
elapsed = time.time() - start

# The free energy is what the paper's supplements plot to pick the best run of a set
import pickle
history = pickle.load(open(f"{output_dir}/model/history.pkl", "rb"))
free_energy = float(history["free_energy"])

summary = {
	"seed": seed,
	"free_energy": free_energy,
	"wall_clock_seconds": round(elapsed, 1),
	"n_states": 8,
	"output_dir": output_dir,
}
os.makedirs("runs/out", exist_ok=True)
with open(f"runs/out/train_seed{seed:02d}.json", "w") as fh:
	json.dump(summary, fh, indent=1)
print(json.dumps(summary, indent=1))
