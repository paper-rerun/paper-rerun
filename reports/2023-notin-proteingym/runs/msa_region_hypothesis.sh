#!/bin/bash
W=/mnt/e/Ciencia/meio/2023-notin-proteingym
export MPLBACKEND=Agg PYTHONUNBUFFERED=1
for M in "esm2_t6_8M_UR50D ESM2_8M" "esm2_t12_35M_UR50D ESM2_35M"; do
	set -- $M
	flock /mnt/e/Ciencia/.gpu.lock $W/env/.venv/bin/python $W/runs/msa_region_hypothesis.py $W/data/weights/$1.pt $2 86 175 130 128 0 >> $W/runs/logs/msa_region_hypothesis.log 2>&1
done
echo "EXIT $?" >> $W/runs/logs/msa_region_hypothesis.log
