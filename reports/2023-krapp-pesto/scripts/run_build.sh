#!/bin/bash
# Usage: run_build.sh <list> <out.h5> <log>  (medium mode: 6 threads, nice 19)
cd /mnt/e/Ciencia/noturno/2023-krapp-pesto
export OMP_NUM_THREADS=6 MKL_NUM_THREADS=6 PESTO_THREADS=6 MPLBACKEND=Agg
/usr/bin/time -v nice -n 19 env/.venv/bin/python -I scripts/build_subset.py repo "$1" "$2" > "$3" 2>&1
echo "exit $?" >> "$3"
