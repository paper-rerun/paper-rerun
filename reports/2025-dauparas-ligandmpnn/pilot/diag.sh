#!/bin/bash
R=/mnt/e/Ciencia/artigos/2025-dauparas-ligandmpnn
{
	echo "=== time: $(date) ==="
	echo "--- gpu run log ---"
	tail -8 "$R/logs/run_all.log" 2>/dev/null || echo "(none)"
	echo "--- cpu run log ---"
	tail -8 "$R/logs/run_all_cpu.log" 2>/dev/null || echo "(none)"
	echo "--- stats counts ---"
	for t in outputs outputs_cpu; do
		for m in ligand_mpnn protein_mpnn_32 protein_mpnn_48; do
			echo "$t/$m: $(ls "$R/$t/$m/stats/" 2>/dev/null | wc -l)"
		done
	done
	echo "--- seqs counts (cpu ligand) ---"
	ls "$R/outputs_cpu/ligand_mpnn/" 2>/dev/null
	echo "--- processes ---"
	ps -eo pid,etime,pcpu,rss,cmd | grep -E '[r]un\.py|[r]un_benchmark' | cut -c1-140
	echo "--- gpu state ---"
	nvidia-smi --query-gpu=memory.used,utilization.gpu --format=csv,noheader
	echo "--- gpu lock queue ---"
	ps -eo etime,cmd | grep '[f]lock /mnt/e/Ciencia/.gpu.lock' | cut -c1-90
} > "$R/logs/diag.txt" 2>&1
