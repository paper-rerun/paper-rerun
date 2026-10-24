#!/bin/bash
# Corrected averages from the authors' released per-mutant scores (PG_v1.3 zip), same evaluation code as ours
W=/mnt/e/Ciencia/meio/2023-notin-proteingym
mkdir -p $W/runs/results
for C in ESM1b ESM2_8M ESM2_35M ESM2_150M ESM2_650M; do
	$W/env/.venv/bin/python $W/runs/evaluate.py $W/sources/authors_esm_scores $C authors_$C $W/runs/results/authors_${C}_per_assay.csv
done | tee $W/runs/results/authors_scores_summary.log
