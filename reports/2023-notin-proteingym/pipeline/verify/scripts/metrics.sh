#!/bin/bash
W=/mnt/e/Ciencia/pipeline/2023-notin-proteingym
"$W/verify/env/venv/bin/python" -I "$W/verify/scripts/metrics.py" --selftest
"$W/verify/env/venv/bin/python" -I "$W/verify/scripts/metrics.py" "$W/repo" "$W/verify"
