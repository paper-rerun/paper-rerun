#!/bin/bash
# Usage: run_model.sh <name> <checkpoint file> <model_type> <strategy> <window> [first] [last]
# Restartable: finished assays are skipped. GPU work under the shared lock
W=/mnt/e/Ciencia/meio/2023-notin-proteingym
NAME=$1; CKPT=$W/data/weights/$2; TYPE=$3; STRATEGY=$4; WINDOW=$5; FIRST=${6:-0}; LAST=${7:-216}
export MPLBACKEND=Agg PYTHONUNBUFFERED=1
# The ESM-1b loader imports proteingym as a package (the authors pip install the repo); same effect
export PYTHONPATH=$W/repo
mkdir -p $W/runs/scores/$NAME $W/runs/logs
cd $W/runs
flock /mnt/e/Ciencia/.gpu.lock $W/env/.venv/bin/python $W/runs/score_driver.py $CKPT $TYPE $STRATEGY $WINDOW $W/runs/scores/$NAME $FIRST $LAST >> $W/runs/logs/$NAME.log 2>&1
echo "EXIT $? $NAME" >> $W/runs/logs/$NAME.log
