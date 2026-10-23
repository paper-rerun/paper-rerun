#!/bin/bash
# Both models inside ONE flock, so we queue for the shared GPU once instead of per chunk.
set -u
R=/mnt/e/Ciencia/artigos/2025-dauparas-ligandmpnn
cd "$R"
export OMP_NUM_THREADS=4
export MPLBACKEND=Agg  # nothing here plots, but no job of ours may open a desktop window
# Torch import off a Windows drive costs about a minute, so keep the chunks big: stats are
# written per structure, so a chunk that dies only loses the structures it had not reached.
# Order matters - the first two are the comparison the paper is about.
for m in ligand_mpnn protein_mpnn_32 protein_mpnn_48; do
	echo "=== $m $(date +%H:%M:%S) ==="
	.venv/bin/python run_benchmark.py --model_type "$m" --chunk 60
done
echo "=== all done $(date +%H:%M:%S) ==="
