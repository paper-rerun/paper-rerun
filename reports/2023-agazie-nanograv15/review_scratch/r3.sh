#!/bin/bash
W=/mnt/e/Ciencia/noturno/2023-agazie-nanograv15
export MPLBACKEND=Agg OMP_NUM_THREADS=4 OPENBLAS_NUM_THREADS=4 MKL_NUM_THREADS=4
cd $W/review_scratch
nice -n 19 $W/env/venv/bin/python -I r3.py $W
