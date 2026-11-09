#!/bin/bash
# Run the TI diagnostic under the same limits
W=/mnt/e/Ciencia/noturno/2023-agazie-nanograv15-cego
export OMP_NUM_THREADS=6 OPENBLAS_NUM_THREADS=6 MKL_NUM_THREADS=6 MPLBACKEND=Agg
cd $W/outputs
nice -n 19 $W/env/venv/bin/python $W/scripts/diagnose_ti.py
