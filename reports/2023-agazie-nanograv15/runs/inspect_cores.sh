#!/bin/bash
W=/mnt/e/Ciencia/noturno/2023-agazie-nanograv15
export MPLBACKEND=Agg OMP_NUM_THREADS=6 OPENBLAS_NUM_THREADS=6
cd $W/runs
nice -n 19 $W/env/venv/bin/python -I inspect_cores.py $W/sources/repo/tutorials/presampled_cores
