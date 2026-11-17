#!/bin/bash
R=/mnt/e/Ciencia/noturno/2025-kovacs-maceoff-cego
cd $R
OMP_NUM_THREADS=1 nice -n 19 env/venv/bin/python -I scripts/analyse.py $R data/test/x/test_large_neut_all.xyz $1 > logs/analyse_$2.log 2>&1
sha256sum claims.json >> logs/analyse_$2.log
cat logs/analyse_$2.log
