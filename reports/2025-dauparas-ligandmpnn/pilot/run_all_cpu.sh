#!/bin/bash
# Same settings as run_all.sh, forced onto the CPU and capped at 4 threads, so it needs no
# GPU lock. Insurance against the shared GPU staying busy; also a device cross-check.
set -u
R=/mnt/e/Ciencia/artigos/2025-dauparas-ligandmpnn
cd "$R"
export CUDA_VISIBLE_DEVICES=
export OMP_NUM_THREADS=4 MKL_NUM_THREADS=4
export MPLBACKEND=Agg  # nothing here plots, but no job of ours may open a desktop window
export LMPNN_OUT_ROOT="$R/outputs_cpu"
for m in ligand_mpnn protein_mpnn_32 protein_mpnn_48; do
	echo "=== $m $(date +%H:%M:%S) ==="
	.venv/bin/python run_benchmark.py --model_type "$m" --chunk 60
done
echo "=== cpu all done $(date +%H:%M:%S) ==="
