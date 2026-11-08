#!/bin/bash
cd /mnt/e/Ciencia/noturno/2023-krapp-pesto-cego
export OMP_NUM_THREADS=4 MKL_NUM_THREADS=4 OPENBLAS_NUM_THREADS=4 N_THREADS=4 MPLBACKEND=Agg
nice -n 19 .venv/bin/python -I scripts/pesto_rerun.py \
  --sids work/masif_sids.txt --mode all_ba --out out/masif.jsonl \
  --masif-json work/masif_pred_per_res.json --keep-scores
