cd /mnt/e/Ciencia/noturno/2022-takamoto-pdebench
nice -n 19 env/.venv/bin/python runs/compare.py 2>&1 | tee runs/compare.log
