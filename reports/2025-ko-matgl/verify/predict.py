# Blind verify: run the three ANI-1x-Subset PES models (matgl v1.3.0, weights from verify/repo at the tag) on COMP6 v1
# Writes one npz per (model, file) under verify/preds, skipped if it already exists, so the run can restart
# Usage: python predict.py [--batch-atoms N] [--single] [--files a.h5 b.h5] [--max-conf N] [--out DIR]
import argparse
import os
import time

import dgl
import h5py
import numpy as np
import torch
from ase import Atoms
from ase.units import Hartree

import matgl
from matgl.ext.ase import Atoms2Graph

Root = "/mnt/e/Ciencia/pipeline/2025-ko-matgl"
VerifyDir = f"{Root}/verify"
DataDir = f"{Root}/data/COMP6v1"
ModelNames = ["M3GNet", "TensorNet", "SO3Net"]
AllFiles = [
	"ANI-MD/ani_md_bench.h5",
	"DrugBank/drugbank_testset.h5",
	"GDB07to09/gdb11_07_test500.h5",
	"GDB07to09/gdb11_08_test500.h5",
	"GDB07to09/gdb11_09_test500.h5",
	"GDB10to13/gdb11_10_test500.h5",
	"GDB10to13/gdb11_11_test500.h5",
	"GDB10to13/gdb13_12_test1000.h5",
	"GDB10to13/gdb13_13_test1000.h5",
	"Tripeptides/tripeptide_full.h5",
	"s66x8/s66x8_wb97x6-31gd.h5",
]


def ReadAllConformations(FilePath):
	# Every group that holds 'species' is one molecule; h5py visits in name order, so the order is stable
	Molecules = []
	with h5py.File(FilePath, "r") as DataFile:
		GroupNames = []
		DataFile.visititems(lambda Name, Item: GroupNames.append(Name) if isinstance(Item, h5py.Group) and "species" in Item else None)
		for GroupName in GroupNames:
			Group = DataFile[GroupName]
			Species = [Symbol.decode() if isinstance(Symbol, bytes) else str(Symbol) for Symbol in Group["species"][()]]
			Molecules.append({
				"name": GroupName,
				"species": Species,
				"coordinates": Group["coordinates"][()].astype(np.float64),
				"energies_ev": Group["energies"][()].astype(np.float64) * Hartree,
				# COMP6 stores dE/dR: check_sign_unit.py gave r = -0.98 to -0.998 and slope -0.99 to -1.005 on 2 molecules x 3 models,
				# so per force_sign_rule the sign is flipped here and the unit stays Ha/A
				"forces_ev": -Group["forces"][()].astype(np.float64) * Hartree,
			})
	return Molecules


def RunBatch(Potential, GraphList, LatticeList, Device):
	BatchGraph = dgl.batch(GraphList).to(Device)
	BatchLattice = torch.cat(LatticeList).to(Device)
	# Default state attr is [0.0, 0.0] for these models; Potential handles a batch of graphs
	StateAttr = torch.zeros((len(GraphList), 2), dtype=matgl.float_th, device=Device)
	Result = Potential(BatchGraph, BatchLattice, StateAttr)
	Energies = Result[0].detach().cpu().double().numpy().reshape(-1)
	Forces = Result[1].detach().cpu().double().numpy()
	del BatchGraph, Result
	return Energies, Forces


def Main():
	Parser = argparse.ArgumentParser()
	Parser.add_argument("--batch-atoms", type=int, default=1500)
	# SO3Net peaks at about 4.8 GB for one 312-atom TrpCage graph (11236 edges), so its batches are capped by edge count;
	# 1500 atoms per batch went past the 8 GB card on 2026-10-25 and ended in 'CUDA error: device not ready'
	Parser.add_argument("--batch-edges", type=int, default=0, help="also cap edges per batch, 0 = no cap")
	Parser.add_argument("--single", action="store_true", help="one conformation per forward pass")
	Parser.add_argument("--files", nargs="*", default=AllFiles)
	Parser.add_argument("--models", nargs="*", default=ModelNames)
	Parser.add_argument("--max-conf", type=int, default=0, help="per molecule, 0 = all")
	Parser.add_argument("--out", default=f"{VerifyDir}/preds")
	Args = Parser.parse_args()
	Device = "cuda"

	Potentials = {}
	for ModelName in Args.models:
		Potential = matgl.load_model(f"{VerifyDir}/repo/pretrained_models/{ModelName}-ANI-1x-Subset-PES")
		Potential = Potential.to(Device)
		Potential.eval()
		Potentials[ModelName] = Potential
	ElementTypes = Potentials[Args.models[0]].model.element_types
	Cutoff = Potentials[Args.models[0]].model.cutoff
	for ModelName, Potential in Potentials.items():
		assert tuple(Potential.model.element_types) == tuple(ElementTypes) and Potential.model.cutoff == Cutoff, ModelName
	print("element_types", ElementTypes, "cutoff", Cutoff, flush=True)
	Converter = Atoms2Graph(ElementTypes, Cutoff)

	for RelativeFile in Args.files:
		Stem = os.path.splitext(os.path.basename(RelativeFile))[0]
		Pending = [ModelName for ModelName in Args.models if not os.path.exists(f"{Args.out}/{ModelName}/{Stem}.npz")]
		if not Pending:
			print("skip", Stem, flush=True)
			continue
		StartTime = time.time()
		Molecules = ReadAllConformations(f"{DataDir}/{RelativeFile}")

		# Flat list of conformations, graphs built once and shared by the three models
		Records = []
		for Molecule in Molecules:
			NumConf = Molecule["coordinates"].shape[0]
			if Args.max_conf:
				NumConf = min(NumConf, Args.max_conf)
			for ConfIndex in range(NumConf):
				MoleculeAtoms = Atoms(symbols=Molecule["species"], positions=Molecule["coordinates"][ConfIndex], pbc=False)
				Graph, Lattice, _ = Converter.get_graph(MoleculeAtoms)
				Records.append((Molecule, ConfIndex, Graph, Lattice))
		print(Stem, "conformations", len(Records), "graphs built in", round(time.time() - StartTime, 1), "s", flush=True)

		# Batches by atom budget, in file order
		Batches = []
		Current = []
		CurrentAtoms = 0
		CurrentEdges = 0
		for RecordIndex, Record in enumerate(Records):
			NumAtoms = len(Record[0]["species"])
			NumEdges = Record[2].num_edges()
			bOverEdges = Args.batch_edges > 0 and CurrentEdges + NumEdges > Args.batch_edges
			if Current and (Args.single or CurrentAtoms + NumAtoms > Args.batch_atoms or bOverEdges):
				Batches.append(Current)
				Current = []
				CurrentAtoms = 0
				CurrentEdges = 0
			Current.append(RecordIndex)
			CurrentAtoms += NumAtoms
			CurrentEdges += NumEdges
		if Current:
			Batches.append(Current)

		for ModelName in Pending:
			ModelStart = time.time()
			Potential = Potentials[ModelName]
			EnergyPred = np.zeros(len(Records))
			ForcePredParts = [None] * len(Records)
			print(ModelName, Stem, "batches", len(Batches), flush=True)
			for Batch in Batches:
				Energies, Forces = RunBatch(Potential, [Records[Index][2] for Index in Batch], [Records[Index][3] for Index in Batch], Device)
				Offset = 0
				for Position, Index in enumerate(Batch):
					NumAtoms = len(Records[Index][0]["species"])
					EnergyPred[Index] = Energies[Position]
					ForcePredParts[Index] = Forces[Offset:Offset + NumAtoms]
					Offset += NumAtoms
				assert Offset == Forces.shape[0]
			torch.cuda.empty_cache()

			# Per conformation stats; raw predicted forces kept too, so any other metric can be recomputed later
			NumAtomsArray = np.array([len(Record[0]["species"]) for Record in Records])
			EnergyDft = np.array([Record[0]["energies_ev"][Record[1]] for Record in Records])
			ForceAbsSum = np.zeros(len(Records))
			ForceNormSum = np.zeros(len(Records))
			for Index, Record in enumerate(Records):
				ForceError = ForcePredParts[Index] - Record[0]["forces_ev"][Record[1]]
				ForceAbsSum[Index] = np.abs(ForceError).sum()
				ForceNormSum[Index] = np.linalg.norm(ForceError, axis=1).sum()
			os.makedirs(f"{Args.out}/{ModelName}", exist_ok=True)
			np.savez(
				f"{Args.out}/{ModelName}/{Stem}.npz",
				group=np.array([Record[0]["name"] for Record in Records]),
				conf_index=np.array([Record[1] for Record in Records]),
				natoms=NumAtomsArray,
				e_dft=EnergyDft,
				e_pred=EnergyPred,
				f_abs_sum=ForceAbsSum,
				f_norm_sum=ForceNormSum,
				f_pred=np.concatenate(ForcePredParts).astype(np.float32),
			)
			print(ModelName, Stem, "done in", round(time.time() - ModelStart, 1), "s", flush=True)


if __name__ == "__main__":
	Main()
