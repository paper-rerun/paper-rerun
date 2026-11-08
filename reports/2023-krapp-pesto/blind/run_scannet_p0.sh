#!/bin/bash
cd /mnt/e/Ciencia/noturno/2023-krapp-pesto-cego
export OMP_NUM_THREADS=2 MKL_NUM_THREADS=2 OPENBLAS_NUM_THREADS=2 N_THREADS=2 MPLBACKEND=Agg
nice -n 19 .venv/bin/python -I scripts/pesto_rerun.py   --sids work/scannet_sids_p0.txt --mode first_ba --out out/scannet_p0.jsonl
