source /mnt/e/Ciencia/noturno/2025-ko-matgl/env/activate.sh
python -I runs/scripts/comp6_eval.py check --model SO3Net --h5 data/COMP6/COMP6v1/s66x8/s66x8_wb97x6-31gd.h5 --out runs/dbg --n 5 --device cpu 2>&1 | grep -v Warn | tail -15
