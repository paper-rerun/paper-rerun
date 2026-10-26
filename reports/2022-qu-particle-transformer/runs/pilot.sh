#!/bin/bash
# Pilot: ParT fp32 on one file per class (*_100.root), then score
HERE=/mnt/e/Ciencia/noturno/2022-qu-particle-transformer
export MPLBACKEND=Agg
bash $HERE/runs/predict.sh ParT fp32 $HERE/runs/pilot_ParT_fp32 $HERE/data/JetClass/test_20M _100.root
cd $HERE/runs
$HERE/env/.venv/bin/python -I score.py $HERE/runs/pilot_ParT_fp32 ParT $HERE/runs/pilot_ParT_fp32/score.json --pilot
