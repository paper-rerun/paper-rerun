#!/bin/bash
W=/mnt/e/Ciencia/pipeline/2023-notin-proteingym
export MPLBACKEND=Agg
flock /mnt/e/Ciencia/.gpu.lock "$W/verify/env/venv/bin/python" "$W/verify/scripts/bench.py" "$W/repo/proteingym/baselines/esm" "$W/data/weights"
