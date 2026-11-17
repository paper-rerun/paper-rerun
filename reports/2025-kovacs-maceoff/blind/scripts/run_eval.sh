#!/bin/bash
# usage: run_eval.sh small|medium|large max_atoms_per_batch
set -eu
R=/mnt/e/Ciencia/noturno/2025-kovacs-maceoff-cego
export OMP_NUM_THREADS=6 MKL_NUM_THREADS=6 MPLBACKEND=Agg
cd $R
nice -n 19 /usr/bin/time -v env/venv/bin/python -I scripts/evaluate.py repo/mace_off23/MACE-OFF23_$1.model data/test/x/test_large_neut_all.xyz runs/$1 $2 >> logs/eval_$1.log 2>&1
