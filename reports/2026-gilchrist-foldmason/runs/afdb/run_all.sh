#!/bin/bash
# Light mode: CPU only, nice 19, 1 thread per FoldMason call, 4 clusters at a time (4 processes max)
# Restartable: run_cluster.sh skips any output that already exists
export OMP_NUM_THREADS=4 MKL_NUM_THREADS=4 OPENBLAS_NUM_THREADS=4 NUMEXPR_NUM_THREADS=4 MPLBACKEND=Agg
ROOT=/mnt/e/Ciencia/noturno/2026-gilchrist-foldmason
HERE=$ROOT/runs/afdb
"$ROOT/env/bioconda/mamba/envs/foldmason/bin/foldmason" version > "$HERE/foldmason_version.txt" 2>&1
find "$ROOT/data/afdb_clusters" -mindepth 1 -maxdepth 1 -type d | sort |
	nice -n 19 xargs -I{} -P4 bash "$HERE/run_cluster.sh" {}
echo "exit $?"
# Collect LDDT with the authors' awk parser
find "$HERE/out" -mindepth 2 -maxdepth 2 -name '*.html' | sort | while read -r html
do
	awk -f "$ROOT/sources/analysis/extractLDDT.awk" "$html"
done > "$HERE/our_afdb_scores.tsv"
wc -l "$HERE/our_afdb_scores.tsv"
