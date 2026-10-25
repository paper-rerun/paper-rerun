# Smallest GPU example: load the three ANI-1x-Subset PES models from data/weights (the v1.3.0 files),
# run one ANI-MD conformation (Caffeine, frame 0) on the GPU and print energy and forces next to the DFT values.
# Not a result, only a check that the stack runs. Units: COMP6 Ha and Ha/A times ase.units.Hartree
import sys

import h5py
import numpy as np
import torch
from ase import Atoms
from ase.units import Hartree

import matgl
from matgl.ext.ase import Atoms2Graph

ROOT = "/mnt/e/Ciencia/pipeline/2025-ko-matgl"
DEVICE = "cuda"

print("python", sys.version.split()[0], "torch", torch.__version__, "cuda", torch.version.cuda, "matgl", matgl.__version__)
import dgl

print("dgl", dgl.__version__, "gpu", torch.cuda.get_device_name(0))

with h5py.File(f"{ROOT}/data/COMP6v1/ANI-MD/ani_md_bench.h5", "r") as DataFile:
	Group = None
	def FindCaffeine(Name, Item):
		global Group
		if Group is None and isinstance(Item, h5py.Group) and "species" in Item and "Caffeine" in Name:
			Group = Name
	DataFile.visititems(FindCaffeine)
	Species = [Symbol.decode() for Symbol in DataFile[Group]["species"][()]]
	Coordinates = DataFile[Group]["coordinates"][0]
	EnergyDft = float(DataFile[Group]["energies"][0]) * Hartree
	ForcesDft = DataFile[Group]["forces"][0].astype(np.float64) * Hartree

MoleculeAtoms = Atoms(symbols=Species, positions=Coordinates)
NumAtoms = len(MoleculeAtoms)
print("group", Group, "atoms", NumAtoms, "E_DFT(eV)", EnergyDft)

for ModelName in ["M3GNet", "TensorNet", "SO3Net"]:
	Potential = matgl.load_model(f"{ROOT}/data/weights/{ModelName}-ANI-1x-Subset-PES")
	Potential = Potential.to(DEVICE)
	Potential.eval()
	ElementTypes = Potential.model.element_types
	Cutoff = Potential.model.cutoff
	Graph, Lattice, StateDefault = Atoms2Graph(ElementTypes, Cutoff).get_graph(MoleculeAtoms)
	Graph = Graph.to(DEVICE)
	Lattice = Lattice.to(DEVICE)
	StateAttr = torch.tensor(StateDefault, dtype=matgl.float_th, device=DEVICE)
	Result = Potential(Graph, Lattice, StateAttr)
	EnergyPred = Result[0].detach().cpu().double().item()
	ForcesPred = Result[1].detach().cpu().double().numpy()
	EnergyErrorPerAtomMeV = abs(EnergyPred - EnergyDft) / NumAtoms * 1000.0
	ForceMae = np.abs(ForcesPred - ForcesDft).mean()
	ForceCorrelation = np.corrcoef(ForcesPred.ravel(), ForcesDft.ravel())[0, 1]
	print(f"{ModelName:9s} device={Result[0].device} cutoff={Cutoff} E_pred={EnergyPred:.4f} eV  |dE|/atom={EnergyErrorPerAtomMeV:.3f} meV  F_MAE={ForceMae:.4f} eV/A  r(F)={ForceCorrelation:.4f}")
print("smoke test done")
