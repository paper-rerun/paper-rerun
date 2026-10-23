#!/bin/bash
R=/mnt/e/Ciencia/artigos/2025-dauparas-ligandmpnn
{
	echo "=== ls outputs_cpu/ligand_mpnn ==="
	ls -la "$R/outputs_cpu/ligand_mpnn/"
	echo "=== ls outputs/ligand_mpnn ==="
	ls -la "$R/outputs/ligand_mpnn/"
	echo "=== cpu log ==="
	cat "$R/logs/run_all_cpu.log"
	echo "=== gpu log ==="
	cat "$R/logs/run_all.log"
	echo "=== cpu chunk errors (last 60 lines) ==="
	tail -60 "$R/outputs_cpu/ligand_mpnn/chunk_errors.log" 2>&1
	echo "=== gpu chunk errors (last 60 lines) ==="
	tail -60 "$R/outputs/ligand_mpnn/chunk_errors.log" 2>&1
} > "$R/logs/d2.txt" 2>&1
