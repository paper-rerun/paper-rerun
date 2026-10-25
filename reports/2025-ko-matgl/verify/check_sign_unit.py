# Pre-batch check (force_sign_rule): sign and Ha/A scale of COMP6 forces vs model forces on 2 molecules,
# one ANI-MD drug (Caffeine) and one GDB molecule (first group of gdb11_09), 16 conformations each.
# Also compares batched vs one-at-a-time forward passes, to make sure batching does not change the numbers.
import json

import numpy as np
import torch

import matgl
from matgl.ext.ase import Atoms2Graph
from ase import Atoms

from predict import DataDir, ReadAllConformations, RunBatch, VerifyDir

Device = "cuda"
NumConf = 16
Picks = [("ANI-MD/ani_md_bench.h5", "Caffeine"), ("GDB07to09/gdb11_09_test500.h5", None)]
Report = {}

for ModelName in ["M3GNet", "TensorNet", "SO3Net"]:
	Potential = matgl.load_model(f"{VerifyDir}/repo/pretrained_models/{ModelName}-ANI-1x-Subset-PES").to(Device)
	Potential.eval()
	Converter = Atoms2Graph(Potential.model.element_types, Potential.model.cutoff)
	for RelativeFile, NameHint in Picks:
		Molecules = ReadAllConformations(f"{DataDir}/{RelativeFile}")
		Molecule = next(Item for Item in Molecules if NameHint is None or NameHint in Item["name"])
		Graphs = []
		Lattices = []
		for ConfIndex in range(NumConf):
			Graph, Lattice, _ = Converter.get_graph(Atoms(symbols=Molecule["species"], positions=Molecule["coordinates"][ConfIndex], pbc=False))
			Graphs.append(Graph)
			Lattices.append(Lattice)
		# One at a time
		SingleEnergies = []
		SingleForces = []
		for Graph, Lattice in zip(Graphs, Lattices):
			Energies, Forces = RunBatch(Potential, [Graph], [Lattice], Device)
			SingleEnergies.append(Energies[0])
			SingleForces.append(Forces)
		SingleEnergies = np.array(SingleEnergies)
		SingleForces = np.concatenate(SingleForces)
		# All 16 in one batch
		BatchEnergies, BatchForces = RunBatch(Potential, Graphs, Lattices, Device)

		ForcesDft = Molecule["forces_ev"][:NumConf].reshape(-1, 3)
		EnergyDft = Molecule["energies_ev"][:NumConf]
		NumAtoms = len(Molecule["species"])
		PredFlat = SingleForces.ravel()
		DftFlat = ForcesDft.ravel()
		Pearson = float(np.corrcoef(PredFlat, DftFlat)[0, 1])
		SlopeThroughOrigin = float((PredFlat * DftFlat).sum() / (DftFlat * DftFlat).sum())
		Key = f"{ModelName}|{Molecule['name']}"
		Report[Key] = {
			"natoms": NumAtoms,
			"pearson_r": Pearson,
			"slope_through_origin": SlopeThroughOrigin,
			"energy_err_per_atom_meV_mean": float(((SingleEnergies - EnergyDft) / NumAtoms * 1000).mean()),
			"energy_abs_err_per_atom_meV_mean": float((np.abs(SingleEnergies - EnergyDft) / NumAtoms * 1000).mean()),
			"force_mae_eV_A": float(np.abs(SingleForces - ForcesDft).mean()),
			"batch_vs_single_max_dE_eV": float(np.abs(BatchEnergies - SingleEnergies).max()),
			"batch_vs_single_max_dF_eV_A": float(np.abs(BatchForces - SingleForces).max()),
		}
		print(Key, json.dumps(Report[Key]), flush=True)
	del Potential
	torch.cuda.empty_cache()

with open(f"{VerifyDir}/check_sign_unit.json", "w") as OutFile:
	json.dump(Report, OutFile, indent=1)
