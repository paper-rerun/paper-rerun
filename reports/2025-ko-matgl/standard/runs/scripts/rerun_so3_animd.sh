source /mnt/e/Ciencia/noturno/2025-ko-matgl/env/activate.sh
export OMP_NUM_THREADS=8 MKL_NUM_THREADS=8
python -I runs/scripts/comp6_eval.py run --model SO3Net --h5 data/COMP6/COMP6v1/ANI-MD/ani_md_bench.h5 --out runs/out_main --mode calc --device cpu > runs/logs/main_SO3Net_ani_md_bench.log 2>&1
echo "exit=$?"
