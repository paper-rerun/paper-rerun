# M3GNet-ANI-1x-Subset-PES predictions on every conformation of the 11 COMP6 v1 files
# One structure at a time (batch of 1, like PESCalculator). Restartable: one npz per molecule group,
# written atomically, skipped if it already exists
import os
import sys
import time

import h5py
import numpy as np

sys.path.insert(0, "/mnt/e/Ciencia/pipeline/2025-ko-matgl/exec/comp6-m3gnet")
from common import DATA_DIR, FILES, OUT_DIR, DecodeSpecies, EvaluateOneStructure, ListMoleculeGroups, LoadPotential, MakeGraphConverter

DEVICE = "cuda"
Potential = LoadPotential(DEVICE)
GraphConverter = MakeGraphConverter(Potential)

for FileName in FILES:
	FileStem = os.path.splitext(os.path.basename(FileName))[0]
	PredictionDir = f"{OUT_DIR}/pred/{FileStem}"
	os.makedirs(PredictionDir, exist_ok=True)
	FileStartTime = time.time()
	ConformationsDone = 0
	ConformationsFailed = 0
	with h5py.File(f"{DATA_DIR}/{FileName}", "r") as DataFile:
		GroupNames = ListMoleculeGroups(DataFile)
		for GroupIndex, GroupName in enumerate(GroupNames):
			GroupOutputPath = f"{PredictionDir}/{GroupIndex:05d}.npz"
			if os.path.exists(GroupOutputPath):
				continue
			Species = DecodeSpecies(DataFile[GroupName]["species"][()])
			AllCoordinates = DataFile[GroupName]["coordinates"][()]
			NumConformations = AllCoordinates.shape[0]
			EnergiesPredicted = np.full(NumConformations, np.nan, dtype=np.float64)
			ForcesPredicted = np.full(AllCoordinates.shape, np.nan, dtype=np.float32)
			ErrorMessages = []
			for ConformationIndex in range(NumConformations):
				# A structure the model cannot evaluate stays NaN and gets reported, not dropped
				try:
					Energy, Forces = EvaluateOneStructure(Potential, GraphConverter, Species, AllCoordinates[ConformationIndex], DEVICE)
					EnergiesPredicted[ConformationIndex] = Energy
					ForcesPredicted[ConformationIndex] = Forces
				except Exception as Error:
					ErrorMessages.append(f"{ConformationIndex}: {Error!r}")
					ConformationsFailed += 1
			TemporaryPath = GroupOutputPath + ".tmp.npz"
			np.savez(TemporaryPath, group=GroupName, energies_pred_eV=EnergiesPredicted, forces_pred_eV_A=ForcesPredicted, errors=np.array(ErrorMessages, dtype=str))
			os.replace(TemporaryPath, GroupOutputPath)
			ConformationsDone += NumConformations
			if GroupIndex % 50 == 0:
				print(f"{FileStem} group {GroupIndex}/{len(GroupNames)} {GroupName} conf_done={ConformationsDone} {time.time() - FileStartTime:.0f}s", flush=True)
	print(f"FILE DONE {FileStem}: {ConformationsDone} new conformations, {ConformationsFailed} failed, {time.time() - FileStartTime:.0f}s", flush=True)
print("ALL DONE")
