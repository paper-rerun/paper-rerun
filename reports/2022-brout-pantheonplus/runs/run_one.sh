#!/bin/bash
# One fit, one thread, lowest priority. Usage: run_one.sh <run_name>
# A lock directory keeps two queues from running the same fit
source /mnt/e/Ciencia/noturno/2022-brout-pantheonplus/env/activate.sh
export OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1
cd runs
mkdir -p logs out
if [ -f "out/$1.json" ]; then exit 0; fi
mkdir "out/$1.lock" 2>/dev/null || { echo "$1 locked by another queue, skipped" >> logs/queue_status.txt; exit 0; }
nice -n 19 python run_fit.py "$1" > "logs/$1.log" 2>&1
echo "$1 exit $?" >> logs/queue_status.txt
rmdir "out/$1.lock"
