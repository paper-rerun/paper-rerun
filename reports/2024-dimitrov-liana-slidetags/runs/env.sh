# Sourced by every run script: light mode (4 threads, CPU only, no windows)
export OMP_NUM_THREADS=4 MKL_NUM_THREADS=4 OPENBLAS_NUM_THREADS=4 NUMEXPR_NUM_THREADS=4 NUMBA_NUM_THREADS=4
export MPLBACKEND=Agg CUDA_VISIBLE_DEVICES=""
export PYTHONHASHSEED=0 PYTHONUNBUFFERED=1
export NUMBA_CACHE_DIR=$HOME/.cache/numba-liana-slidetags
PY="nice -n 19 $HOME/venvs/liana-slidetags/bin/python"
R=/mnt/e/Ciencia/noturno/2024-dimitrov-liana-slidetags
DATA=$R/data/slidetags
