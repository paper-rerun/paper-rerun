#!/bin/bash
W=/mnt/e/Ciencia/pipeline/2023-notin-proteingym
"$W/verify/env/venv/bin/python" -I "$W/verify/scripts/impute_650M.py" "$W/repo" "$W/verify"
