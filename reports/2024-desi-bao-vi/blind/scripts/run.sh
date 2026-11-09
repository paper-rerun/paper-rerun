#!/bin/bash
# Usage: run.sh <logname> <args for desi_bao.py>
cd /mnt/e/Ciencia/noturno/2024-desi-bao-vi-cego
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 MPLBACKEND=Agg
LOG=logs/$1.log; shift
echo "$(date -Is) start: python -I scripts/desi_bao.py $*" >> "$LOG"
nice -n 19 /usr/bin/time -v env/venv/bin/python -I scripts/desi_bao.py "$@" >> "$LOG" 2>&1
RC=$?
echo "$(date -Is) end rc=$RC" >> "$LOG"
tail -40 "$LOG"
