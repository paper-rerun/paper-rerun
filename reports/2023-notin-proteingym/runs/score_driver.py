"""Run the authors' compute_fitness.main() over a range of DMS indices with one model load.

Same arguments the authors' scoring_ESM*_substitutions.sh scripts pass. The only change is
environment-level: load_model_and_alphabet is memoized so the checkpoint is read from disk once,
not once per assay. Assays whose output csv already exists are skipped, so the run is restartable.

Usage: score_driver.py <checkpoint> <model_type> <scoring_strategy> <scoring_window> <out_dir> <first> <last>
"""
import os
import sys
import time

REPO = "/mnt/e/Ciencia/meio/2023-notin-proteingym/repo"
sys.path.insert(0, REPO + "/proteingym/baselines/esm")
sys.path.insert(0, REPO + "/proteingym")
import compute_fitness

# Cache the loaded model so each assay reuses it
OriginalLoad = compute_fitness.pretrained.load_model_and_alphabet
LoadedModels = {}


def CachedLoad(ModelLocation):
	if ModelLocation not in LoadedModels:
		LoadedModels[ModelLocation] = OriginalLoad(ModelLocation)
	return LoadedModels[ModelLocation]


compute_fitness.pretrained.load_model_and_alphabet = CachedLoad

Checkpoint, ModelType, ScoringStrategy, ScoringWindow, OutDir, FirstIndex, LastIndex = sys.argv[1:8]
Reference = REPO + "/reference_files/DMS_substitutions.csv"
DmsFolder = "/mnt/e/Ciencia/meio/2023-notin-proteingym/data/dms/DMS_ProteinGym_substitutions"
os.makedirs(OutDir, exist_ok=True)

import pandas as pd
DmsIds = pd.read_csv(Reference)["DMS_id"]

for DmsIndex in range(int(FirstIndex), int(LastIndex) + 1):
	OutputFile = OutDir + os.sep + DmsIds[DmsIndex] + ".csv"
	# Skip what a previous run already finished
	if os.path.exists(OutputFile):
		continue
	StartTime = time.time()
	Arguments = [
		"--model-location", Checkpoint,
		"--model_type", ModelType,
		"--dms_index", str(DmsIndex),
		"--dms_mapping", Reference,
		"--dms-input", DmsFolder,
		"--dms-output", OutDir + os.sep + "tmp",
		"--scoring-strategy", ScoringStrategy,
		"--scoring-window", ScoringWindow,
	]
	Parsed = compute_fitness.create_parser().parse_args(Arguments)
	# Write into a temp folder first so a cut run never leaves a half file that looks finished
	compute_fitness.main(Parsed)
	os.replace(OutDir + os.sep + "tmp" + os.sep + DmsIds[DmsIndex] + ".csv", OutputFile)
	print(f"DONE {DmsIndex} {DmsIds[DmsIndex]} {time.time() - StartTime:.1f}s", flush=True)
