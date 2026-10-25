# Unit and sign check before the batch (definition force_sign_rule)
# Two molecules: ANI-MD Caffeine and the first molecule of gdb11_09, all their conformations
# r = Pearson between model forces and COMP6 forces*Hartree, slope = least squares through the origin
import json
import sys

import h5py
import numpy as np
from ase.units import Hartree

sys.path.insert(0, "/mnt/e/Ciencia/pipeline/2025-ko-matgl/exec/comp6-so3net")
from common import DATA_DIR, OUT_DIR, DecodeSpecies, EvaluateOneStructure, ListMoleculeGroups, LoadPotential, MakeGraphConverter

DEVICE = "cuda"
Potential = LoadPotential(DEVICE)
GraphConverter = MakeGraphConverter(Potential)

CheckReport = {"hartree_eV": Hartree, "molecules": []}
for FileName, NameFilter in [("ANI-MD/ani_md_bench.h5", "Caffeine"), ("GDB07to09/gdb11_09_test500.h5", None)]:
	with h5py.File(f"{DATA_DIR}/{FileName}", "r") as DataFile:
		GroupNames = ListMoleculeGroups(DataFile)
		ChosenGroup = [Name for Name in GroupNames if NameFilter is None or NameFilter in Name][0]
		Species = DecodeSpecies(DataFile[ChosenGroup]["species"][()])
		AllCoordinates = DataFile[ChosenGroup]["coordinates"][()]
		EnergiesDft = DataFile[ChosenGroup]["energies"][()].astype(np.float64) * Hartree
		ForcesDft = DataFile[ChosenGroup]["forces"][()].astype(np.float64) * Hartree
	ForcesModelList = []
	EnergyOffsets = []
	for ConformationIndex in range(len(AllCoordinates)):
		EnergyPredicted, ForcesPredicted = EvaluateOneStructure(Potential, GraphConverter, Species, AllCoordinates[ConformationIndex], DEVICE)
		ForcesModelList.append(ForcesPredicted.astype(np.float64))
		EnergyOffsets.append(EnergyPredicted - EnergiesDft[ConformationIndex])
	ForcesModel = np.stack(ForcesModelList).ravel()
	ForcesReference = ForcesDft.ravel()
	PearsonR = float(np.corrcoef(ForcesModel, ForcesReference)[0, 1])
	SlopeThroughOrigin = float((ForcesModel * ForcesReference).sum() / (ForcesReference * ForcesReference).sum())
	NumAtoms = len(Species)
	MoleculeReport = {
		"file": FileName, "group": ChosenGroup, "n_atoms": NumAtoms, "n_conf": len(AllCoordinates),
		"pearson_r": PearsonR, "slope_through_origin": SlopeThroughOrigin,
		"force_mae_stored_sign_eV_A": float(np.abs(ForcesModel - ForcesReference).mean()),
		"force_mae_flipped_sign_eV_A": float(np.abs(ForcesModel + ForcesReference).mean()),
		"mean_signed_energy_error_meV_per_atom": float(np.mean(EnergyOffsets) / NumAtoms * 1000.0),
		"energy_mae_meV_per_atom": float(np.mean(np.abs(EnergyOffsets)) / NumAtoms * 1000.0),
	}
	CheckReport["molecules"].append(MoleculeReport)
	print(json.dumps(MoleculeReport))

# Apply the rule: sign from r, unit from |slope|
AllR = [Molecule["pearson_r"] for Molecule in CheckReport["molecules"]]
AllSlopes = [abs(Molecule["slope_through_origin"]) for Molecule in CheckReport["molecules"]]
if all(R > 0.9 for R in AllR):
	CheckReport["sign_decision"] = "keep"
elif all(R < -0.9 for R in AllR):
	CheckReport["sign_decision"] = "flip"
else:
	CheckReport["sign_decision"] = "STOP"
CheckReport["unit_decision"] = "Ha/A ok" if all(0.8 <= Slope <= 1.25 for Slope in AllSlopes) else "STOP"
print("sign:", CheckReport["sign_decision"], "unit:", CheckReport["unit_decision"])
json.dump(CheckReport, open(f"{OUT_DIR}/signcheck.json", "w"), indent=1)
