# Cross-check: matgl's own ASE PESCalculator on 3 conformations vs the stored run.py predictions
import sys, h5py, numpy as np
from ase import Atoms
sys.path.insert(0, "/mnt/e/Ciencia/pipeline/2025-ko-matgl/exec/comp6-tensornet")
from common import DATA_DIR, OUT_DIR, DecodeSpecies, ListMoleculeGroups, LoadPotential
from matgl.ext.ase import PESCalculator
Potential = LoadPotential("cpu")
Calculator = PESCalculator(Potential)
for FileName, Stem in [("ANI-MD/ani_md_bench.h5", "ani_md_bench"), ("GDB10to13/gdb13_13_test1000.h5", "gdb13_13_test1000"), ("DrugBank/drugbank_testset.h5", "drugbank_testset")]:
	with h5py.File(f"{DATA_DIR}/{FileName}", "r") as DataFile:
		GroupName = ListMoleculeGroups(DataFile)[5]
		Species = DecodeSpecies(DataFile[GroupName]["species"][()])
		Coordinates = DataFile[GroupName]["coordinates"][3]
	MoleculeAtoms = Atoms(symbols=Species, positions=Coordinates)
	MoleculeAtoms.calc = Calculator
	Stored = np.load(f"{OUT_DIR}/pred/{Stem}/00005.npz")
	print(Stem, GroupName, "E_calc_cpu", MoleculeAtoms.get_potential_energy(), "E_run_gpu", Stored["energies_pred_eV"][3], "max|dF|", np.abs(MoleculeAtoms.get_forces() - Stored["forces_pred_eV_A"][3]).max())
