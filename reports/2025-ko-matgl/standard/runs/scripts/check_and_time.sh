source /mnt/e/Ciencia/noturno/2025-ko-matgl/env/activate.sh
H=data/COMP6/COMP6v1
flock /mnt/e/Ciencia/.gpu.lock bash -c "
for m in M3GNet SO3Net TensorNet; do
  python -I runs/scripts/comp6_eval.py check --model \$m --h5 $H/ANI-MD/ani_md_bench.h5 --out runs/out --n 50 2>/dev/null
done
time python -I runs/scripts/comp6_eval.py run --model M3GNet --h5 $H/s66x8/s66x8_wb97x6-31gd.h5 --out runs/out_calc_timing --mode calc 2>/dev/null
time python -I runs/scripts/comp6_eval.py run --model M3GNet --h5 $H/s66x8/s66x8_wb97x6-31gd.h5 --out runs/out_batch_timing --mode batch 2>/dev/null
"
