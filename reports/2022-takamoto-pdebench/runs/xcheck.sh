cd /mnt/e/Ciencia/noturno/2022-takamoto-pdebench/runs
OMP_NUM_THREADS=4 MKL_NUM_THREADS=4 OPENBLAS_NUM_THREADS=4 NUMEXPR_NUM_THREADS=4 MPLBACKEND=Agg CUDA_VISIBLE_DEVICES= nice -n 19 taskset -c 8-11 ../env/.venv/bin/python xcheck_adv_fno.py > logs/xcheck_adv_fno.log 2>&1; echo exit $? >> logs/xcheck_adv_fno.log
