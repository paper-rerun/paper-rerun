#!/bin/bash
cd /mnt/e/Ciencia/noturno/2024-desi-bao-vi-cego
export OMP_NUM_THREADS=$2 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 MPLBACKEND=Agg
LOG=logs/$1.log
case $1 in
  cobaya_pointcheck) CMD="env/venv/bin/python -I scripts/cobaya_pointcheck.py" ;;
  cobaya_bbn) CMD="env/venv/bin/cobaya-run -f cobaya/bbn.yaml" ;;
esac
echo "$(date -Is) start: $CMD (OMP_NUM_THREADS=$OMP_NUM_THREADS)" >> "$LOG"
nice -n 19 /usr/bin/time -v $CMD >> "$LOG" 2>&1
RC=$?
echo "$(date -Is) end rc=$RC" >> "$LOG"
tail -30 "$LOG"
