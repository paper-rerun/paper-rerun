#!/bin/bash
W=/mnt/e/Ciencia/pipeline/2023-notin-proteingym
"$W/verify/env/venv/bin/python" -I "$W/verify/scripts/testset_and_mutants.py" "$W/repo" "$W/data" "$W/verify"
