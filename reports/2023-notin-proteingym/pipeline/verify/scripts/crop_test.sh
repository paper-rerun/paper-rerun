#!/bin/bash
# Usage: crop_test.sh <weights name> <ESM1b|ESM2> <output subfolder> <DMS_id ...>
W=/mnt/e/Ciencia/pipeline/2023-notin-proteingym
Name=$1; ModelType=$2; Sub=$3; shift 3
export MPLBACKEND=Agg PYTHONDONTWRITEBYTECODE=1
cd "$W/repo/scripts/scoring_DMS_zero_shot"
flock /mnt/e/Ciencia/.gpu.lock "$W/verify/env/venv/bin/python" -u "$W/verify/scripts/crop_test.py" "$W/repo" "$W/data" "$W/data/weights/$Name.pt" "$W/verify/extra/$Sub" "$ModelType" "$@"
