#!/bin/bash
# Primary run: PESCalculator per conformation (D-SCORING primary path), CPU float32, 10 jobs in parallel.
# Restartable: comp6_eval.py skips (model, file) pairs whose .npz exists.
source /mnt/e/Ciencia/noturno/2025-ko-matgl/env/activate.sh
export OMP_NUM_THREADS=2 MKL_NUM_THREADS=2 OPENBLAS_NUM_THREADS=2
mkdir -p runs/out_main runs/logs
for f in drugbank_testset gdb13_13_test1000 gdb13_12_test1000 gdb11_11_test500 gdb11_10_test500 gdb11_09_test500 gdb11_08_test500 gdb11_07_test500 ani_md_bench tripeptide_full s66x8_wb97x6-31gd; do
  for m in M3GNet TensorNet SO3Net; do echo "$m $(find data/COMP6 -name "$f.h5")"; done
done | xargs -P 10 -L 1 bash -c 'python -I runs/scripts/comp6_eval.py run --model $0 --h5 $1 --out runs/out_main --mode calc --device cpu > runs/logs/main_$0_$(basename $1 .h5).log 2>&1; echo "exit=$? $0 $1"'
echo ALL_DONE
