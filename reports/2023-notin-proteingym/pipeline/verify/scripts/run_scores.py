# Runs the authors' compute_fitness.main() once per assay, with the same flags as their scoring_ESM1b / scoring_ESM2 scripts.
# Only change vs calling the shell script 217 times: the checkpoint is loaded once per process (cached), not once per assay.
# Skips assays whose output csv already exists, so the run can be restarted
import os, sys, time
import functools
import pandas as pd

Repo = sys.argv[1]
ModelName = sys.argv[2]
Checkpoint = sys.argv[3]
OutputFolder = sys.argv[4]
OrderPath = sys.argv[5]
AssayCount = int(sys.argv[6])

# Same import setup as "python ../../proteingym/baselines/esm/compute_fitness.py"
sys.path.insert(0, f"{Repo}/proteingym/baselines/esm")
# The v1 checkpoint loader (ESM-1b) imports proteingym.baselines.esm, so the repo root has to be importable too (same as pip install -e .)
sys.path.append(Repo)
import compute_fitness

# Load each checkpoint once, then hand back the same model to every main() call
compute_fitness.pretrained.load_model_and_alphabet = functools.lru_cache(maxsize=1)(compute_fitness.pretrained.load_model_and_alphabet)

ReferencePath = f"{Repo}/reference_files/DMS_substitutions.csv"
DataFolder = os.environ["DMS_DATA_FOLDER"]
Reference = pd.read_csv(ReferencePath)
Order = pd.read_csv(OrderPath)
os.makedirs(OutputFolder, exist_ok=True)

for DmsIndex in Order["dms_index"].values[:AssayCount]:
	DmsId = Reference["DMS_id"][DmsIndex]
	OutputPath = f"{OutputFolder}/{DmsId}.csv"
	if os.path.exists(OutputPath):
		continue

	# Flags copied from scoring_ESM1b_substitutions.sh / scoring_ESM2_substitutions.sh
	if ModelName == "ESM1b":
		Flags = ["--model_type", "ESM1b", "--scoring-strategy", "wt-marginals", "--scoring-window", "overlapping"]
	else:
		Flags = ["--scoring-strategy", "masked-marginals", "--model_type", "ESM2"]
	TempFolder = f"{OutputFolder}/_partial"
	Arguments = compute_fitness.create_parser().parse_args(["--model-location", Checkpoint, "--dms_index", str(DmsIndex), "--dms_mapping", ReferencePath, "--dms-input", DataFolder, "--dms-output", TempFolder] + Flags)
	Start = time.time()
	compute_fitness.main(Arguments)
	# Move the finished file in place only after main() wrote it completely
	os.replace(f"{TempFolder}/{DmsId}.csv", OutputPath)
	print(f"DONE {DmsIndex} {DmsId} seq_len {Reference['seq_len'][DmsIndex]} {time.time() - Start:.1f}s", flush=True)
