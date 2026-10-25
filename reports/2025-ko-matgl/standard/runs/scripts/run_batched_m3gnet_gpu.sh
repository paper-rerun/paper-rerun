#!/bin/bash
# Secondary, finishing the batched M3GNet run on the GPU (the CPU batched run used ~8 GB RAM per job and got OOM-killed).
# Only the smaller files: GDB07, GDB08 and S66x8 were already done on CPU by run_batched_m3gnet.sh.
source /mnt/e/Ciencia/noturno/2025-ko-matgl/env/activate.sh
for f in data/COMP6/COMP6v1/ANI-MD/ani_md_bench.h5 data/COMP6/COMP6v1/Tripeptides/tripeptide_full.h5; do
  flock /mnt/e/Ciencia/.gpu.lock python -I runs/scripts/comp6_eval.py run --model M3GNet --h5 $f --out runs/out_batch_m3gnet_4000 --mode batch --device cuda --max-atoms 4000 > runs/logs/batch_gpu_4000_$(basename $f .h5).log 2>&1
  echo "exit=$? $f"
done
echo ALL_DONE
