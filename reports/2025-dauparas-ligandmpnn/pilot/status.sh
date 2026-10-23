#!/bin/bash
R=/mnt/e/Ciencia/artigos/2025-dauparas-ligandmpnn
echo "--- run_all.log tail ---"
tail -6 "$R/logs/run_all.log" 2>/dev/null || echo "(no log yet: still queued for the GPU)"
echo "--- stats counts (of 468) ---"
for m in ligand_mpnn protein_mpnn_32 protein_mpnn_48 ligand_mpnn_nocontext; do
	n=$(ls "$R/outputs/$m/stats/" 2>/dev/null | wc -l)
	echo "$m: $n"
done
echo "--- gpu ---"
nvidia-smi --query-gpu=memory.used,utilization.gpu --format=csv,noheader
echo "--- lock queue ---"
ps -eo etime,cmd | grep '[f]lock /mnt/e/Ciencia/.gpu.lock' | sed 's/\(.\{110\}\).*/\1/'
