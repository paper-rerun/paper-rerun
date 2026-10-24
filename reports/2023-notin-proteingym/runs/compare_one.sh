#!/bin/bash
# Usage: compare_one.sh <run name> <our column> <authors column>
W=/mnt/e/Ciencia/meio/2023-notin-proteingym
$W/env/.venv/bin/python $W/runs/compare_authors.py $W/runs/scores/$1 $W/sources/authors_esm_scores $2 $3 $1 $W/runs/results/$1_vs_authors.csv | tee -a $W/runs/results/vs_authors.log
