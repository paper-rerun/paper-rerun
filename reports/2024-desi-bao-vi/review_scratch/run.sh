cd /mnt/e/Ciencia/noturno/2024-desi-bao-vi
export OMP_NUM_THREADS=4 OPENBLAS_NUM_THREADS=4 MKL_NUM_THREADS=4 MPLBACKEND=Agg
nice -n 19 env/venv/bin/python -I review_scratch/$1
