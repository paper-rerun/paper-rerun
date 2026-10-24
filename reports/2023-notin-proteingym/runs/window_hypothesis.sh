#!/bin/bash
W=/mnt/e/Ciencia/meio/2023-notin-proteingym
export MPLBACKEND=Agg PYTHONUNBUFFERED=1
flock /mnt/e/Ciencia/.gpu.lock $W/env/.venv/bin/python $W/runs/window_hypothesis.py $W/data/weights/esm2_t6_8M_UR50D.pt ESM2_8M 86 175 24 130 128 0 > $W/runs/logs/window_hypothesis_8M.log 2>&1
echo "EXIT $?" >> $W/runs/logs/window_hypothesis_8M.log
