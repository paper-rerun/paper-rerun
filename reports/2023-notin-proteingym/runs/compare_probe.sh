#!/bin/bash
cd /mnt/e/Ciencia/meio/2023-notin-proteingym/runs
for S in wt masked; do
	../env/.venv/bin/python compare_authors.py scores/probe_ESM1b_$S ../sources/authors_esm_scores esm1b_t33_650M_UR50S ESM1b probe_ESM1b_$S
done 2>&1 | tee results/probe_esm1b.log
