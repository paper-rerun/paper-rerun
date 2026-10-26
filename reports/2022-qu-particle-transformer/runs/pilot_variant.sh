#!/bin/bash
# D10 variant on the pilot subset (one file per class, *_100.root): ParT fp32 with weaver-core 0.5.3, then score
HERE=/mnt/e/Ciencia/noturno/2022-qu-particle-transformer
export MPLBACKEND=Agg
bash $HERE/runs/predict_variant_0.5.3.sh ParT fp32 $HERE/runs/pilot_ParT_fp32_weaver0.5.3 $HERE/data/JetClass/test_20M _100.root
cd $HERE/runs
$HERE/env/.venv/bin/python -I score.py $HERE/runs/pilot_ParT_fp32_weaver0.5.3 ParT $HERE/runs/pilot_ParT_fp32_weaver0.5.3/score.json --pilot
