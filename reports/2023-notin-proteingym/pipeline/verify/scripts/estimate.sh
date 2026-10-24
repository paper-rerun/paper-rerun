#!/bin/bash
W=/mnt/e/Ciencia/pipeline/2023-notin-proteingym
"$W/verify/env/venv/bin/python" -I "$W/verify/scripts/estimate.py" "$W/repo/reference_files/DMS_substitutions.csv" "$W/verify/assay_order_seed0.csv"
