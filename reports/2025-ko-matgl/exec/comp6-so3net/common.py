# Shared pieces for the comp6-so3net block: file list, molecule listing and one-structure evaluation
# Evaluation mirrors matgl.ext.ase.PESCalculator.calculate in v1.3.0: Atoms2Graph per structure, batch of 1
import h5py
import numpy as np
import torch
from ase import Atoms

import matgl
from matgl.ext.ase import Atoms2Graph

ROOT = "/mnt/e/Ciencia/pipeline/2025-ko-matgl"
DATA_DIR = f"{ROOT}/data/COMP6v1"
WEIGHTS_DIR = f"{ROOT}/data/weights/SO3Net-ANI-1x-Subset-PES"
OUT_DIR = f"{ROOT}/exec/comp6-so3net"

# Files needed by the claims first, the two extra GDB files (sensitivity readings B and C) last
FILES = [
	"ANI-MD/ani_md_bench.h5",
	"s66x8/s66x8_wb97x6-31gd.h5",
	"Tripeptides/tripeptide_full.h5",
	"DrugBank/drugbank_testset.h5",
	"GDB07to09/gdb11_09_test500.h5",
	"GDB10to13/gdb11_10_test500.h5",
	"GDB10to13/gdb11_11_test500.h5",
	"GDB10to13/gdb13_12_test1000.h5",
	"GDB10to13/gdb13_13_test1000.h5",
	"GDB07to09/gdb11_07_test500.h5",
	"GDB07to09/gdb11_08_test500.h5",
]


def ListMoleculeGroups(DataFile):
	# Every group that holds a 'coordinates' dataset is one molecule, in visit order (sorted by h5py)
	MoleculeGroupNames = []
	def CollectGroup(Name, Item):
		if isinstance(Item, h5py.Group) and "coordinates" in Item:
			MoleculeGroupNames.append(Name)
	DataFile.visititems(CollectGroup)
	return MoleculeGroupNames


def LoadPotential(Device):
	Potential = matgl.load_model(WEIGHTS_DIR)
	Potential = Potential.to(Device)
	Potential.eval()
	return Potential


def EvaluateOneStructure(Potential, GraphConverter, Species, Coordinates, Device):
	# Same path as PESCalculator: graph, lattice and default state from Atoms2Graph, then Potential forward
	MoleculeAtoms = Atoms(symbols=Species, positions=Coordinates)
	Graph, Lattice, StateDefault = GraphConverter.get_graph(MoleculeAtoms)
	Graph = Graph.to(Device)
	Lattice = Lattice.to(Device)
	StateAttr = torch.tensor(StateDefault, dtype=matgl.float_th, device=Device)
	Result = Potential(Graph, Lattice, StateAttr)
	EnergyPredicted = Result[0].detach().cpu().numpy().item()
	ForcesPredicted = Result[1].detach().cpu().numpy()
	return EnergyPredicted, ForcesPredicted


def MakeGraphConverter(Potential):
	return Atoms2Graph(Potential.model.element_types, Potential.model.cutoff)


def DecodeSpecies(RawSpecies):
	return [Symbol.decode() if isinstance(Symbol, bytes) else str(Symbol) for Symbol in RawSpecies]
