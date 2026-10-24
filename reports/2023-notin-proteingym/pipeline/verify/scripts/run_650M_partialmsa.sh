#!/bin/bash
# Extra: released-script 650M run (full sequence, optimal window) on the 3 partial-MSA assays outside the 54-assay sample
W=/mnt/e/Ciencia/pipeline/2023-notin-proteingym
export MPLBACKEND=Agg PYTHONDONTWRITEBYTECODE=1 DMS_DATA_FOLDER=$W/data/DMS_ProteinGym_substitutions
cd "$W/repo/scripts/scoring_DMS_zero_shot"
flock /mnt/e/Ciencia/.gpu.lock "$W/verify/env/venv/bin/python" -u "$W/verify/scripts/run_scores.py" "$W/repo" ESM2 "$W/data/weights/esm2_t33_650M_UR50D.pt" "$W/verify/extra/full_650M_partialmsa" "$W/verify/extra/order_650M_partialmsa.csv" 3
