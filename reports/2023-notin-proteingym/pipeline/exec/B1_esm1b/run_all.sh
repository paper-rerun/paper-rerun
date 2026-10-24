#!/bin/bash
# Score all 217 assays with the authors' ESM-1b script (wt-marginals, overlapping windows), one assay per call
# Restartable: an assay whose score file already exists is skipped. Per-assay timing goes to timing.tsv
# Usage: run_all.sh [first_index] [last_index]
set -u
W=/mnt/e/Ciencia/pipeline/2023-notin-proteingym
Out=$W/exec/B1_esm1b/scores
First=${1:-0}
Last=${2:-216}
# The ESM-1b checkpoint goes through the v1 loader in pretrained.py, which does "from proteingym.baselines.esm import esm".
# That needs the repo package importable, as after "pip install -e ." of the authors' setup.py. We set PYTHONPATH instead of installing
export PYTHONPATH=$W/repo
mkdir -p "$Out/ESM1b" "$W/exec/B1_esm1b/logs"
for DmsIndex in $(seq "$First" "$Last"); do
	# Row DmsIndex+2 of the reference file (header is line 1), DMS_id is column 2
	DmsId=$(sed -n "$((DmsIndex + 2))p" "$W/repo/reference_files/DMS_substitutions.csv" | cut -d, -f2)
	if [ -f "$Out/ESM1b/$DmsId.csv" ]; then
		continue
	fi
	Start=$(date +%s)
	if "$W/run_authors_script.sh" esm1b "$DmsIndex" "$Out" > "$W/exec/B1_esm1b/logs/$DmsIndex.log" 2>&1; then
		Status=ok
	else
		Status=FAIL
	fi
	echo -e "$DmsIndex\t$DmsId\t$Status\t$(( $(date +%s) - Start ))" | tee -a "$W/exec/B1_esm1b/timing.tsv"
done
echo "loop done"
