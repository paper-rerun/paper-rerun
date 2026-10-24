#!/bin/bash
# Usage: eval_one.sh <run name> <score column>
W=/mnt/e/Ciencia/meio/2023-notin-proteingym
mkdir -p $W/runs/results
$W/env/.venv/bin/python $W/runs/evaluate.py $W/runs/scores/$1 $2 $1 $W/runs/results/$1_per_assay.csv | tee -a $W/runs/results/summary.log
