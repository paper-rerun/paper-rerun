# Sensitivity only, not a claim: the same model run in DGL batches instead of one structure at a time
# In v1.3.0 M3GNet the three-body layer indexes the full graph with pruned-graph edge ids (bug fixed in PR #840),
# so in a batch those ids can land on edges of other graphs and the output depends on batch composition.
# Batches here: consecutive conformations in file order, crossing molecule boundaries, like an unshuffled test loader
import json
import os
import sys

import dgl
import h5py
import numpy as np
import torch
from ase import Atoms
from ase.units import Hartree

import matgl

sys.path.insert(0, "/mnt/e/Ciencia/pipeline/2025-ko-matgl/exec/comp6-m3gnet")
from common import DATA_DIR, OUT_DIR, DecodeSpecies, ListMoleculeGroups, LoadPotential, MakeGraphConverter

DEVICE = "cuda"
Potential = LoadPotential(DEVICE)
GraphConverter = MakeGraphConverter(Potential)
SignCheck = json.load(open(f"{OUT_DIR}/signcheck.json"))
ReferenceForceSign = -1.0 if SignCheck["sign_decision"] == "flip" else 1.0
SummaryPath = f"{OUT_DIR}/batched_sensitivity.json"
Summary = json.load(open(SummaryPath)) if os.path.exists(SummaryPath) else {}

for BatchSize in [16, 32]:
	for FileName in ["s66x8/s66x8_wb97x6-31gd.h5", "Tripeptides/tripeptide_full.h5", "ANI-MD/ani_md_bench.h5"]:
		FileStem = os.path.splitext(os.path.basename(FileName))[0]
		ResultKey = f"{FileStem}_bs{BatchSize}"
		if ResultKey in Summary:
			continue
		# Flatten the file into (species, coordinates, E_dft, F_dft, E_single) in file order
		Items = []
		with h5py.File(f"{DATA_DIR}/{FileName}", "r") as DataFile:
			for GroupIndex, GroupName in enumerate(ListMoleculeGroups(DataFile)):
				Species = DecodeSpecies(DataFile[GroupName]["species"][()])
				AllCoordinates = DataFile[GroupName]["coordinates"][()]
				EnergiesDft = DataFile[GroupName]["energies"][()].astype(np.float64) * Hartree
				ForcesDft = ReferenceForceSign * DataFile[GroupName]["forces"][()].astype(np.float64) * Hartree
				SinglePrediction = np.load(f"{OUT_DIR}/pred/{FileStem}/{GroupIndex:05d}.npz")["energies_pred_eV"]
				for ConformationIndex in range(len(AllCoordinates)):
					Items.append((Species, AllCoordinates[ConformationIndex], EnergiesDft[ConformationIndex], ForcesDft[ConformationIndex], SinglePrediction[ConformationIndex]))
		EnergyErrorsPerAtom = []
		DifferencesVsSingle = []
		ForceAbsSum = 0.0
		ForceCount = 0
		for BatchStart in range(0, len(Items), BatchSize):
			BatchItems = Items[BatchStart:BatchStart + BatchSize]
			Graphs = []
			Lattices = []
			States = []
			for Species, Coordinates, _, _, _ in BatchItems:
				Graph, Lattice, StateDefault = GraphConverter.get_graph(Atoms(symbols=Species, positions=Coordinates))
				Graphs.append(Graph)
				Lattices.append(Lattice)
				States.append(torch.tensor(StateDefault, dtype=matgl.float_th))
			BatchedGraph = dgl.batch(Graphs).to(DEVICE)
			Result = Potential(BatchedGraph, torch.cat(Lattices).to(DEVICE), torch.stack(States).to(DEVICE))
			Energies = Result[0].detach().cpu().double().numpy().reshape(-1)
			ForcesPerGraph = torch.split(Result[1].detach().cpu().double(), [len(Item[0]) for Item in BatchItems])
			for Position, (Species, _, EnergyDft, ForceDft, EnergySingle) in enumerate(BatchItems):
				NumAtoms = len(Species)
				EnergyErrorsPerAtom.append(abs(Energies[Position] - EnergyDft) / NumAtoms * 1000.0)
				DifferencesVsSingle.append(abs(Energies[Position] - EnergySingle) / NumAtoms * 1000.0)
				ForceAbsSum += np.abs(ForcesPerGraph[Position].numpy() - ForceDft).sum()
				ForceCount += ForceDft.size
			del Result, BatchedGraph
			torch.cuda.empty_cache()
		Summary[ResultKey] = {"batch_size": BatchSize, "n_conf": len(EnergyErrorsPerAtom), "energy_mae_meV_per_atom": float(np.mean(EnergyErrorsPerAtom)),
			"force_mae_eV_A": ForceAbsSum / ForceCount, "mean_abs_energy_diff_vs_single_meV_per_atom": float(np.mean(DifferencesVsSingle)),
			"max_abs_energy_diff_vs_single_meV_per_atom": float(np.max(DifferencesVsSingle))}
		print(ResultKey, json.dumps(Summary[ResultKey]), flush=True)
		json.dump(Summary, open(SummaryPath, "w"), indent=1)
