#!/bin/bash
# Usage: run_eval.sh <h5> <masif|scannet> <out.csv> <log> [source_data.csv]  (medium mode: 6 threads, nice 19)
cd /mnt/e/Ciencia/noturno/2023-krapp-pesto
export OMP_NUM_THREADS=6 MKL_NUM_THREADS=6 PESTO_THREADS=6 MPLBACKEND=Agg
R=/mnt/e/Ciencia/noturno/2023-krapp-pesto
/usr/bin/time -v nice -n 19 env/.venv/bin/python -I scripts/evaluate.py $R/repo $R/$1 $2 $R/$3 ${5:+$R/$5} > "$4" 2>&1
echo "exit $?" >> "$4"
