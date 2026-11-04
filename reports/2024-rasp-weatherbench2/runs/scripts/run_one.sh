#!/bin/bash
# Run one task by hand, recording the real exit code. Usage: run_one.sh <name> <forecast> <truth> <variable> <level>
cd /mnt/e/Ciencia/noturno/2024-rasp-weatherbench2
export MPLBACKEND=Agg OMP_NUM_THREADS=8 OPENBLAS_NUM_THREADS=8
name=$1
echo "$(date -Is) start $name" >> runs/logs/run_one.log
/usr/bin/time -v env/.venv/bin/python -I runs/scripts/wb2_rmse.py "$2" "$3" "$4" "$5" runs/out/$name >> runs/logs/$name.log 2>&1
rc=$?
echo "$(date -Is) end $name rc=$rc" >> runs/logs/run_one.log
