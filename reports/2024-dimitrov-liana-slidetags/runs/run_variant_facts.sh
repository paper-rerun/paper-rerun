source /mnt/e/Ciencia/noturno/2024-dimitrov-liana-slidetags/runs/env.sh
export OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1 NUMBA_NUM_THREADS=1
cd $R/runs && $PY variant_facts.py
