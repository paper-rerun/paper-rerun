# Cross-check the batched predictions in preds/ against matgl's own ASE calculator (PESCalculator), one conformation at a time
# 4 conformations per (model, file), drawn with seed 20261025; DFT side re-read from the HDF5 file by group name
import json

import h5py
import numpy as np
from ase import Atoms
from ase.units import Hartree

import matgl
from matgl.ext.ase import PESCalculator

from predict import AllFiles, DataDir, VerifyDir

Random = np.random.default_rng(20261025)
Report = []
for ModelName in ["M3GNet", "TensorNet", "SO3Net"]:
	Potential = matgl.load_model(f"{VerifyDir}/repo/pretrained_models/{ModelName}-ANI-1x-Subset-PES")
	Calculator = PESCalculator(Potential)
	for RelativeFile in AllFiles:
		Stem = RelativeFile.split("/")[-1][:-3]
		Pred = np.load(f"{VerifyDir}/preds/{ModelName}/{Stem}.npz")
		Offsets = np.concatenate([[0], np.cumsum(Pred["natoms"])])
		with h5py.File(f"{DataDir}/{RelativeFile}", "r") as DataFile:
			for Index in Random.choice(len(Pred["natoms"]), 4, replace=False):
				Group = DataFile[str(Pred["group"][Index])]
				ConfIndex = int(Pred["conf_index"][Index])
				Species = [Symbol.decode() if isinstance(Symbol, bytes) else str(Symbol) for Symbol in Group["species"][()]]
				MoleculeAtoms = Atoms(symbols=Species, positions=Group["coordinates"][ConfIndex].astype(np.float64), pbc=False)
				MoleculeAtoms.calc = Calculator
				EnergyAse = MoleculeAtoms.get_potential_energy()
				ForcesAse = MoleculeAtoms.get_forces()
				ForcesNpz = Pred["f_pred"][Offsets[Index]:Offsets[Index + 1]]
				EnergyDft = Group["energies"][ConfIndex] * Hartree
				ForcesDft = -Group["forces"][ConfIndex].astype(np.float64) * Hartree
				Row = {
					"model": ModelName, "file": Stem, "index": int(Index), "natoms": len(Species),
					"dE_ase_vs_npz_eV": float(EnergyAse - Pred["e_pred"][Index]),
					"maxdF_ase_vs_npz": float(np.abs(ForcesAse - ForcesNpz).max()),
					"dE_dft_vs_npz_eV": float(EnergyDft - Pred["e_dft"][Index]),
					"ase_E_err_meV_atom": float((EnergyAse - EnergyDft) / len(Species) * 1000),
					"ase_F_mae": float(np.abs(ForcesAse - ForcesDft).mean()),
				}
				Report.append(Row)
				print(json.dumps(Row), flush=True)
with open(f"{VerifyDir}/crosscheck_ase.json", "w") as OutFile:
	json.dump(Report, OutFile, indent=1)
Worst = {Key: max(abs(Row[Key]) for Row in Report) for Key in ["dE_ase_vs_npz_eV", "maxdF_ase_vs_npz", "dE_dft_vs_npz_eV"]}
print("WORST", Worst)
