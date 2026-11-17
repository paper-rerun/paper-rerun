#!/bin/bash
# Run one MACE-OFF23 model over the test file. $1 = small|medium|large
# The user is on this machine, so: nice 19, 6 threads, half the GPU (set in evaluate.py).
set -euo pipefail
cd "$(dirname "$0")/.."
ROOT="$PWD"
KEY="$1"
shift || true

export MPLBACKEND=Agg
export OMP_NUM_THREADS=6
export MKL_NUM_THREADS=6
export PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True

mkdir -p "$ROOT/runs/out" "$ROOT/runs/logs"
/usr/bin/time -v nice -n 19 "$ROOT/env/venv/bin/python" -I "$ROOT/scripts/evaluate.py" \
  --model "$ROOT/weights/MACE-OFF23_${KEY}.model" \
  --xyz "$ROOT/data/test_extract/test_large_neut_all.xyz" \
  --out "$ROOT/runs/out/errors_${KEY}.csv" \
  "$@" 2>&1 | tee "$ROOT/runs/logs/eval_${KEY}.log"
