# Predict energy and forces of one MACE-OFF23 model on every config of the test xyz
# Resumable: results go to one npz per chunk of configs, existing chunks are skipped
import os
import sys
import time

import numpy as np
import torch
import ase.io

from mace import data
from mace.tools import torch_geometric, utils

model_path = sys.argv[1]
xyz_path = sys.argv[2]
out_dir = sys.argv[3]
max_atoms_per_batch = int(sys.argv[4])
configs_per_chunk = 1000

torch.set_num_threads(6)
torch.set_default_dtype(torch.float64)
torch.cuda.set_per_process_memory_fraction(0.5, 0)
device = torch.device("cuda")
os.makedirs(out_dir, exist_ok=True)

model = torch.load(model_path, map_location=device)
model = model.double().to(device)
model.eval()
for parameter in model.parameters():
	parameter.requires_grad = False
z_table = utils.AtomicNumberTable([int(z) for z in model.atomic_numbers])
r_max = float(model.r_max)
print(f"model={model_path} r_max={r_max} z={z_table.zs} dtype={next(model.parameters()).dtype}", flush=True)

atoms_list = ase.io.read(xyz_path, index=":", format="extxyz")
print(f"configs={len(atoms_list)}", flush=True)


def predict_batch(atoms_batch):
	# Build graphs on CPU, run on GPU, return energies and per-config forces
	configs = [data.config_from_atoms(atoms) for atoms in atoms_batch]
	dataset = [data.AtomicData.from_config(config, z_table=z_table, cutoff=r_max) for config in configs]
	loader = torch_geometric.dataloader.DataLoader(dataset=dataset, batch_size=len(dataset), shuffle=False, drop_last=False)
	batch = next(iter(loader)).to(device)
	output = model(batch.to_dict(), compute_force=True, training=False)
	energies = output["energy"].detach().cpu().numpy()
	forces = output["forces"].detach().cpu().numpy()
	pointers = batch.ptr.cpu().numpy()
	forces_per_config = [forces[pointers[i]:pointers[i + 1]] for i in range(len(atoms_batch))]
	return list(energies), forces_per_config


def predict_with_split(atoms_batch):
	# On CUDA OOM, split the batch in half and retry each half
	# Leave the except block before splitting, so the traceback frames release their GPU tensors
	bOutOfMemory = False
	try:
		return predict_batch(atoms_batch)
	except RuntimeError as error:
		if "out of memory" not in str(error).lower():
			raise
		bOutOfMemory = True
	if bOutOfMemory:
		torch.cuda.empty_cache()
		if len(atoms_batch) == 1:
			raise RuntimeError(f"out of memory on a single config of {len(atoms_batch[0])} atoms")
		half = len(atoms_batch) // 2
		print(f"  OOM on {len(atoms_batch)} configs / {sum(len(a) for a in atoms_batch)} atoms, splitting", flush=True)
		energies_first, forces_first = predict_with_split(atoms_batch[:half])
		energies_second, forces_second = predict_with_split(atoms_batch[half:])
		return energies_first + energies_second, forces_first + forces_second


start_time = time.time()
number_of_chunks = (len(atoms_list) + configs_per_chunk - 1) // configs_per_chunk
for chunk_index in range(number_of_chunks):
	chunk_path = os.path.join(out_dir, f"chunk_{chunk_index:04d}.npz")
	if os.path.exists(chunk_path):
		continue
	first = chunk_index * configs_per_chunk
	last = min(first + configs_per_chunk, len(atoms_list))
	chunk_energies = []
	chunk_forces = []
	# Greedy batches capped by total atoms, in file order
	batch = []
	batch_atoms = 0
	for index in range(first, last):
		atoms = atoms_list[index]
		if batch and batch_atoms + len(atoms) > max_atoms_per_batch:
			energies, forces = predict_with_split(batch)
			chunk_energies += energies
			chunk_forces += forces
			batch = []
			batch_atoms = 0
		batch.append(atoms)
		batch_atoms += len(atoms)
	if batch:
		energies, forces = predict_with_split(batch)
		chunk_energies += energies
		chunk_forces += forces
	assert len(chunk_energies) == last - first
	numbers_of_atoms = np.array([len(atoms_list[i]) for i in range(first, last)])
	assert all(len(f) == n for f, n in zip(chunk_forces, numbers_of_atoms))
	temporary_path = chunk_path + ".tmp.npz"
	np.savez(temporary_path, index=np.arange(first, last), n_atoms=numbers_of_atoms,
		energy=np.array(chunk_energies), forces=np.concatenate(chunk_forces))
	os.replace(temporary_path, chunk_path)
	elapsed = time.time() - start_time
	print(f"chunk {chunk_index + 1}/{number_of_chunks} configs {first}-{last - 1} done, {elapsed:.0f}s, peak GPU {torch.cuda.max_memory_allocated() / 1e9:.2f} GB", flush=True)

print("all chunks done", flush=True)
