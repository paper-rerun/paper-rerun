#!/bin/bash
W=/mnt/e/Ciencia/noturno/2023-agazie-nanograv15-cego
export OMP_NUM_THREADS=6 MPLBACKEND=Agg
cd $W/outputs && nice -n 19 $W/env/venv/bin/python $W/scripts/core_meta.py
