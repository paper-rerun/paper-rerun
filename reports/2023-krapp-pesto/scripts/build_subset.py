# Build a PeSTo dataset h5 from a list of biounit files, with the authors' processing/build_dataset.py functions
# The loop is the __main__ block of build_dataset.py at ba651aa, with: our file list, device cpu, no DataLoader workers, sorted order, a log line per file
# Usage: python build_subset.py <repo_dir> <file_list.txt> <out.h5>
import os
import re
import sys

import h5py
import numpy as np
import torch as pt

repo_dir, list_path, out_path = sys.argv[1], sys.argv[2], sys.argv[3]
sys.path.insert(0, os.path.join(repo_dir, "processing"))
import build_dataset as bd
from src.dataset import StructuresDataset
from src.structure import clean_structure, tag_hetatm_chains, split_by_chain, filter_non_atomic_subunits, remove_duplicate_tagged_subunits
from src.data_encoding import config_encoding, extract_all_contacts

pt.set_num_threads(int(os.environ.get("PESTO_THREADS", "6")))
config_dataset = bd.config_dataset
pdb_filepaths = sorted(set(line.strip() for line in open(list_path) if line.strip()))
dataset = StructuresDataset(pdb_filepaths, with_preprocessing=False)
device = pt.device("cpu")

with h5py.File(out_path, "w", libver="latest") as hf:
	# Store dataset encoding
	for key in config_encoding:
		hf[f"metadata/{key}"] = config_encoding[key].astype(np.string_)
	hf["metadata/mids"] = config_dataset["molecule_ids"].astype(np.string_)

	metadata_l = []
	for i in range(len(dataset)):
		structure, pdb_filepath = dataset[i]
		name = os.path.basename(pdb_filepath)
		if structure is None:
			print(f"SKIP read_error {name}", flush=True)
			continue

		m = re.match(r".*/([a-z0-9]*)\.pdb([0-9]*)\.gz", pdb_filepath)
		pdbid = m[1]
		bid = m[2]

		# Same filters, same order as the authors
		if structure["xyz"].shape[0] >= config_dataset["max_num_atoms"]:
			print(f"SKIP too_many_atoms {name} {structure['xyz'].shape[0]}", flush=True)
			continue
		structure = clean_structure(structure)
		structure = tag_hetatm_chains(structure)
		subunits = split_by_chain(structure)
		subunits = filter_non_atomic_subunits(subunits)
		if len(subunits) < 2:
			print(f"SKIP monomer {name}", flush=True)
			continue
		subunits = remove_duplicate_tagged_subunits(subunits)
		contacts = extract_all_contacts(subunits, config_dataset["r_thr"], device=device)
		if len(contacts) == 0:
			print(f"SKIP no_contacts {name}", flush=True)
			continue
		structures_data, contacts_data = bd.pack_dataset_items(subunits, contacts, config_dataset["molecule_ids"], config_dataset["max_num_nn"], device=device)
		metadata = bd.store_dataset_items(hf, pdbid, bid, structures_data, contacts_data)
		metadata_l.extend(metadata)
		print(f"OK {name} items={len(set(md['key'] for md in metadata))}", flush=True)

	hf["metadata/keys"] = np.array([m["key"] for m in metadata_l]).astype(np.string_)
	hf["metadata/sizes"] = np.array([m["size"] for m in metadata_l])
	hf["metadata/ckeys"] = np.array([m["ckey"] for m in metadata_l]).astype(np.string_)
	hf["metadata/ctypes"] = np.stack(np.where(np.array([m["ctype"] for m in metadata_l])), axis=1).astype(np.uint32)
print("done", len(metadata_l), "contact records")
