#!/bin/bash -e
# FoldMason path: bioconda build foldmason-4.dd3c235-h5021889_0 (the GitHub release binary was refused by the local permission system)
# One AFDB cluster, the FoldMason commands of the authors' align_family.sh (default and --fast only)
# plus msa2lddtreport on both MSAs against the default run's structure DB, all single-thread
# Usage: run_cluster.sh <cluster dir>
FOLDMASON=/mnt/e/Ciencia/noturno/2026-gilchrist-foldmason/env/bioconda/mamba/envs/foldmason/bin/foldmason
DIR="$1"
PDB=$(realpath "${DIR}/pdbs/")
OUT=/mnt/e/Ciencia/noturno/2026-gilchrist-foldmason/runs/afdb/out/$(basename "$DIR")
mkdir -p "$OUT"

# Default mode
if [ ! -s "${OUT}/foldmason_aa.fa" ]
then
	rm -rf "${OUT}/foldmason_tmp"
	/usr/bin/time -o "${OUT}/foldmason.time" -f "Wall clock time (seconds): %e" \
		"$FOLDMASON" easy-msa "$PDB" "${OUT}/foldmason" "${OUT}/foldmason_tmp" --threads 1 > "${OUT}/foldmason.log" 2>&1
fi

# Fast mode
if [ ! -s "${OUT}/foldmason_fast_aa.fa" ]
then
	rm -rf "${OUT}/foldmason_fast_tmp"
	/usr/bin/time -o "${OUT}/foldmason_fast.time" -f "Wall clock time (seconds): %e" \
		"$FOLDMASON" easy-msa "$PDB" "${OUT}/foldmason_fast" "${OUT}/foldmason_fast_tmp" --threads 1 --fast > "${OUT}/foldmason_fast.log" 2>&1
fi

# LDDT of both MSAs on the default run's structure DB, full MSA (no --only-scoring-cols)
DB="${OUT}/foldmason_tmp/latest/structures"
for TOOL in foldmason foldmason_fast
do
	if [ ! -s "${OUT}/${TOOL}.html" ]
	then
		"$FOLDMASON" msa2lddtreport "$DB" "${OUT}/${TOOL}_aa.fa" "${OUT}/${TOOL}.html" --threads 1 > "${OUT}/${TOOL}_lddt.log" 2>&1
	fi
done
