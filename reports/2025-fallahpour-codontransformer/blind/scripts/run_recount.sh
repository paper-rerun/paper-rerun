#!/bin/bash
set -euo pipefail
cd /mnt/e/Ciencia/noturno/2025-fallahpour-codontransformer-cego
export OMP_NUM_THREADS=4 MKL_NUM_THREADS=4 MPLBACKEND=Agg
/usr/bin/time -v nice -n 19 ./venv/bin/python -I scripts/recount.py \
  "data/extracted/Source Data/Fig. 4, Supplementary Fig. 19f-h, 20, 21, 22 and 25.xlsx" \
  results_recount.json
