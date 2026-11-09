#!/bin/bash
# Run the analysis with 6 threads max, lowest priority, Agg backend
W=/mnt/e/Ciencia/noturno/2023-agazie-nanograv15-cego
export OMP_NUM_THREADS=6 OPENBLAS_NUM_THREADS=6 MKL_NUM_THREADS=6 MPLBACKEND=Agg
cd $W/outputs
sha256sum -c $W/claims.json.sha256 --status 2>/dev/null || (cd $W && sha256sum claims.json)
nice -n 19 $W/env/venv/bin/python $W/scripts/analyze.py
