#!/bin/bash
# Secondary (not verdict): M3GNet through one batched Potential call, as a training/validation loop would.
# In matgl 1.3.0 the three-body indices are misaligned when threebody_cutoff < cutoff (fixed by PR #840),
# so the output depends on how molecules are batched. Two batch sizes show the size of that effect.
source /mnt/e/Ciencia/noturno/2025-ko-matgl/env/activate.sh
export OMP_NUM_THREADS=2 MKL_NUM_THREADS=2 OPENBLAS_NUM_THREADS=2
mkdir -p runs/logs
for size in 4000; do
  for f in $(find data/COMP6 -name '*.h5' | sort); do echo "$size $f"; done
done | xargs -P 4 -L 1 bash -c 'python -I runs/scripts/comp6_eval.py run --model M3GNet --h5 $1 --out runs/out_batch_m3gnet_$0 --mode batch --device cpu --max-atoms $0 > runs/logs/batch_$0_$(basename $1 .h5).log 2>&1; echo "exit=$? $0 $1"'
echo ALL_DONE
