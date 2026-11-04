#!/bin/bash
# Maize with the 2020-09-10 liliopsida lineage the author shared in compleasm#70. Same command as run_one.sh, other -L
set -uo pipefail
ROOT=/mnt/e/Ciencia/noturno/2023-huang-compleasm
OUT=$ROOT/runs/zmay_author2020
export OMP_NUM_THREADS=8 MKL_NUM_THREADS=8 OPENBLAS_NUM_THREADS=8 NUMEXPR_NUM_THREADS=8 MPLBACKEND=Agg
mkdir -p "$OUT"; cd "$OUT"
echo "start $(date -Is) lineage md5 04fe88de47726ab0304a0d5d39b3a7c0" | tee "$OUT/run.log"
/usr/bin/time -v -o "$OUT/time.txt" nice -n 19 "$ROOT/env/.venv/bin/python" "$ROOT/env/bin/compleasm.py" run \
	-a "$ROOT/data/genomes/GCF_902167145.1_Zm-B73-REFERENCE-NAM-5.0_genomic.fna.gz" -o "$OUT" -t 8 -l liliopsida_odb10 -L "$ROOT/author_lineage_2020/mb" \
	--outs 0.95 \
	--miniprot_execute_path "$ROOT/env/bin/miniprot" --hmmsearch_execute_path "$ROOT/env/bin/hmmsearch" >> "$OUT/run.log" 2>&1
RC=$?
echo "end $(date -Is) rc=$RC" | tee -a "$OUT/run.log"
