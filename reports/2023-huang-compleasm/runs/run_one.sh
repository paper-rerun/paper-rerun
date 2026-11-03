#!/bin/bash
# Usage: run_one.sh <tag> <assembly basename> <lineage> [outs]
# Runs compleasm v0.2.2 busco mode, -t 8, nice 19. Restartable: skips if summary.txt exists
set -uo pipefail
ROOT=/mnt/e/Ciencia/noturno/2023-huang-compleasm
TAG=$1; ASM=$2; LIN=$3; OUTS=${4:-0.95}
OUT=$ROOT/runs/$TAG
export OMP_NUM_THREADS=8 MKL_NUM_THREADS=8 OPENBLAS_NUM_THREADS=8 NUMEXPR_NUM_THREADS=8 MPLBACKEND=Agg
if [ -s "$OUT/summary.txt" ]; then echo "$TAG already done"; exit 0; fi
# Wait until the lineage is extracted and the genome passed its size and md5 check
until [ -f "$ROOT/data/mb_downloads/$LIN.done" ] && grep -q "^${ASM}_genomic.fna.gz.*OK$" "$ROOT/data/download_check.tsv"; do sleep 30; done
mkdir -p "$OUT"
cd "$OUT"
echo "start $(date -Is) tag=$TAG asm=$ASM lineage=$LIN outs=$OUTS" | tee "$OUT/run.log"
/usr/bin/time -v -o "$OUT/time.txt" nice -n 19 "$ROOT/env/.venv/bin/python" "$ROOT/env/bin/compleasm.py" run \
	-a "$ROOT/data/genomes/${ASM}_genomic.fna.gz" -o "$OUT" -t 8 -l "$LIN" -L "$ROOT/data/mb_downloads" \
	--outs "$OUTS" \
	--miniprot_execute_path "$ROOT/env/bin/miniprot" --hmmsearch_execute_path "$ROOT/env/bin/hmmsearch" >> "$OUT/run.log" 2>&1
RC=$?
echo "end $(date -Is) rc=$RC" | tee -a "$OUT/run.log"
exit $RC
