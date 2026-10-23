#!/bin/bash
# Score the models under all three readings of "near the ligand".
# $@ = model labels to score.
R=/mnt/e/Ciencia/artigos/2025-dauparas-ligandmpnn
cd "$R"
export OMP_NUM_THREADS=4 MKL_NUM_THREADS=4 MPLBACKEND=Agg
for c in all metal largest; do
	echo "########## context=$c ##########"
	.venv/bin/python score_recovery.py "$@" --context "$c" --out "recovery_$c.json" 2>&1 |
		grep -vE 'pkg_resources|ProDy|UserWarning|^  import'
done
