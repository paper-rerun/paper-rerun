#!/bin/bash
# Stop the CPU insurance run: the GPU run has the lock and is much faster, and both
# hammering /mnt/e at once slows each other down. Partial CPU stats are kept as a
# device cross-check.
R=/mnt/e/Ciencia/artigos/2025-dauparas-ligandmpnn
for p in $(pgrep -f "LMPNN_OUT_ROOT|run_all_cpu.sh"); do
	kill "$p" 2>/dev/null
done
# the driver and its child, found by the cpu output root in the environment
for p in $(pgrep -f "run_benchmark.py --model_type"); do
	if tr '\0' '\n' < "/proc/$p/environ" 2>/dev/null | grep -q "LMPNN_OUT_ROOT=$R/outputs_cpu"; then
		echo "killing cpu driver $p"
		pkill -P "$p" 2>/dev/null
		kill "$p" 2>/dev/null
	fi
done
sleep 3
echo "remaining:"
ps -eo pid,etime,cmd | grep -E '[r]un_benchmark|[r]un\.py' | cut -c1-120
echo "cpu stats: $(ls "$R/outputs_cpu/ligand_mpnn/stats/" 2>/dev/null | wc -l)"
