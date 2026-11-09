#!/bin/bash
W=/mnt/e/Ciencia/noturno/2023-agazie-nanograv15-cego
export OMP_NUM_THREADS=6 OPENBLAS_NUM_THREADS=6 MKL_NUM_THREADS=6 MPLBACKEND=Agg
cd $W && sha256sum -c claims.json.sha256 && sha256sum history/nano15_hd_chain_fg_long_050523.npy
cd $W/outputs && nice -n 19 $W/env/venv/bin/python $W/scripts/c1_history.py
