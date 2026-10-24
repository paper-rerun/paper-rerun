# Extra analysis: do the authors' released scores for the long assays match a run on the MSA-cropped sequence?
# Runs the authors' compute_fitness.main() without --dms_index, giving target_seq[MSA_start-1:MSA_end] and offset MSA_start
# Usage: crop_test.py <repo> <data folder> <checkpoint> <output folder> <ESM1b|ESM2> <DMS_id> [<DMS_id> ...]
import os, sys
import pandas as pd

Repo, DataFolder, Checkpoint, OutputFolder, ModelType = sys.argv[1:6]
sys.path.insert(0, f"{Repo}/proteingym/baselines/esm")
sys.path.append(Repo)
import compute_fitness

Reference = pd.read_csv(f"{Repo}/reference_files/DMS_substitutions.csv").set_index("DMS_id")
os.makedirs(OutputFolder, exist_ok=True)
for DmsId in sys.argv[6:]:
	Assay = Reference.loc[DmsId]
	CroppedSequence = Assay["target_seq"][int(Assay["MSA_start"]) - 1:int(Assay["MSA_end"])]
	if ModelType == "ESM1b":
		Flags = ["--model_type", "ESM1b", "--scoring-strategy", "wt-marginals", "--scoring-window", "overlapping"]
	else:
		Flags = ["--scoring-strategy", "masked-marginals", "--model_type", "ESM2"]
	Arguments = compute_fitness.create_parser().parse_args(["--model-location", Checkpoint, "--dms-input", f"{DataFolder}/DMS_ProteinGym_substitutions/{Assay['DMS_filename']}", "--dms-output", OutputFolder, "--target_seq", CroppedSequence, "--offset-idx", str(int(Assay["MSA_start"]))] + Flags)
	compute_fitness.main(Arguments)
	print("DONE", DmsId, "cropped length", len(CroppedSequence), flush=True)
