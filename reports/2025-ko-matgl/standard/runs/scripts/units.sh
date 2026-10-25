source /mnt/e/Ciencia/noturno/2025-ko-matgl/env/activate.sh
flock /mnt/e/Ciencia/.gpu.lock python -I runs/scripts/comp6_eval.py units --out runs/out
