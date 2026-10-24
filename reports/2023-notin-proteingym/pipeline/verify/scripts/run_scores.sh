#!/bin/bash
# Usage: run_scores.sh <esm1b|8M|35M|150M|650M> <number of assays from the fixed-seed order>
set -eu
W=/mnt/e/Ciencia/pipeline/2023-notin-proteingym
case "$1" in
	esm1b) Name=esm1b_t33_650M_UR50S; Folder=ESM1b; Model=ESM1b ;;
	8M) Name=esm2_t6_8M_UR50D; Folder=ESM2/8M; Model=ESM2 ;;
	35M) Name=esm2_t12_35M_UR50D; Folder=ESM2/35M; Model=ESM2 ;;
	150M) Name=esm2_t30_150M_UR50D; Folder=ESM2/150M; Model=ESM2 ;;
	650M) Name=esm2_t33_650M_UR50D; Folder=ESM2/650M; Model=ESM2 ;;
	*) echo "unknown model $1"; exit 1 ;;
esac
export MPLBACKEND=Agg
export PYTHONDONTWRITEBYTECODE=1
export DMS_DATA_FOLDER=$W/data/DMS_ProteinGym_substitutions
cd "$W/repo/scripts/scoring_DMS_zero_shot"
flock /mnt/e/Ciencia/.gpu.lock "$W/verify/env/venv/bin/python" -u "$W/verify/scripts/run_scores.py" "$W/repo" "$Model" "$W/data/weights/$Name.pt" "$W/verify/scores/$Folder" "$W/verify/assay_order_seed0.csv" "$2"
