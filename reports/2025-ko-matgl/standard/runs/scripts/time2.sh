source /mnt/e/Ciencia/noturno/2025-ko-matgl/env/activate.sh
H=data/COMP6/COMP6v1
export OMP_NUM_THREADS=2 MKL_NUM_THREADS=2
time python -I runs/scripts/comp6_eval.py run --model M3GNet --h5 $H/s66x8/s66x8_wb97x6-31gd.h5 --out runs/t_cpu_calc --mode calc --device cpu 2>&1 | grep -E "done|Error"
flock /mnt/e/Ciencia/.gpu.lock bash -c "
time python -I runs/scripts/comp6_eval.py run --model M3GNet --h5 $H/s66x8/s66x8_wb97x6-31gd.h5 --out runs/t_gpu_batch --mode batch 2>&1 | grep -E 'done|Error'
python -I runs/scripts/comp6_eval.py check --model SO3Net --h5 $H/ANI-MD/ani_md_bench.h5 --out runs/t_dbg --n 50 2>&1 | grep -v Warn | tail -8
"
