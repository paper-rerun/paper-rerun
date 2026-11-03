cd /mnt/e/Ciencia/noturno/2022-takamoto-pdebench
OMP_NUM_THREADS=4 nice -n 19 env/.venv/bin/python runs/check_ckpts.py claims.json 2>&1 | tee runs/logs_check_ckpts.txt
