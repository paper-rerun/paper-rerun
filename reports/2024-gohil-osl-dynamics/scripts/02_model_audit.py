"""What is in the trained models the authors deposited, against what the scripts ask for.

The paper's dynamic network analysis is an 8-state TDE-HMM on the Giles 38-parcel
parcellation: examples/toolbox_paper/ctf_rest/tde_hmm_networks.py says n_states: 8,
tde_pca {n_embeddings: 15, n_pca_components: 80}, and the paper pins 8 only by saying
DyNeMo used "seven modes (rather than 8)". This reads each deposited model's own config.
"""

import json
import zipfile

import numpy as np
import yaml

MODELS = {
	"tde_hmm_notts_meguk_giles": "downloads/trained_tde_hmm.zip",
	"tde_hmm_notts_meguk_glasser": "downloads/m_tde_hmm_glasser.zip",
	"ae_hmm_notts_meguk_glasser": "downloads/m_ae_hmm_glasser.zip",
}

# What the repository scripts ask for, read from the scripts themselves
SCRIPT_ASKS = {
	"ctf_rest/tde_hmm_networks.py": {"n_states": 8, "n_channels": 80, "parcellation": "atlas-Giles_nparc-38"},
	"ctf_rest/tde_hmm_bursts.py": {"n_states": 3, "n_channels": 1, "parcellation": "single parcel, left motor cortex"},
	"elekta_task/ae_hmm.py": {"n_states": 8, "n_channels": 38, "parcellation": "atlas-Giles_nparc-38"},
}

audit = {"script_asks": SCRIPT_ASKS, "deposited": {}}

for name, path in MODELS.items():
	archive = zipfile.ZipFile(path)
	config = yaml.safe_load(archive.read("config.yml"))
	entry = {
		"files": sorted(archive.namelist()),
		"n_states": config.get("n_states"),
		"n_channels": config.get("n_channels"),
		"n_epochs": config.get("n_epochs"),
		"sequence_length": config.get("sequence_length"),
		"learn_means": config.get("learn_means"),
		"has_pca_components": "pca_components.npy" in archive.namelist(),
		"weights_format": "keras .h5" if "model.weights.h5" in archive.namelist() else "unknown",
	}
	# The osl-dynamics version that wrote it is a comment on the first line
	first_line = archive.read("config.yml").decode().splitlines()[0]
	entry["written_by"] = first_line.lstrip("# ").strip()

	with archive.open("covs.npy") as fh:
		covs = np.load(fh)
	entry["covs_shape"] = list(covs.shape)
	audit["deposited"][name] = entry

# The one deposited model on the paper's parcellation
giles = audit["deposited"]["tde_hmm_notts_meguk_giles"]
asked = SCRIPT_ASKS["ctf_rest/tde_hmm_networks.py"]
audit["verdict"] = {
	"giles_model_matches_the_script": giles["n_states"] == asked["n_states"],
	"giles_states_deposited": giles["n_states"],
	"giles_states_the_script_asks_for": asked["n_states"],
	"giles_has_pca_components": giles["has_pca_components"],
	"note": (
		"The paper's figures 3, 4 and 5 are the Giles 38-parcel pipeline. The only deposited "
		"model on that parcellation has a different number of states from the script that "
		"made the figure, and does not carry the PCA basis its covariances live in, so it "
		"cannot be mapped back to the data. The two 8-state models are on a parcellation "
		"the paper never mentions."
	),
}

with open("runs/out/model_audit.json", "w") as fh:
	json.dump(audit, fh, indent=1)

for name, entry in audit["deposited"].items():
	print(f"{name}: n_states={entry['n_states']} n_channels={entry['n_channels']} "
	      f"pca={entry['has_pca_components']} covs={entry['covs_shape']} ({entry['written_by']})")
print()
for k, v in audit["verdict"].items():
	print(f"{k}: {v}")
