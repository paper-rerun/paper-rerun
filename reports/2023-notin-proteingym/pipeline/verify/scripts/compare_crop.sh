#!/bin/bash
W=/mnt/e/Ciencia/pipeline/2023-notin-proteingym
"$W/verify/env/venv/bin/python" -I "$W/verify/scripts/compare_crop.py" "$W/data" "$@"
