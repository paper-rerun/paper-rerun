#!/bin/bash
# Compare the bioconda-build AFDB run with the authors' scores (split complete / reduced, see compare.py)
ROOT=/mnt/e/Ciencia/noturno/2026-gilchrist-foldmason
cd "$ROOT/runs/afdb"
nice -n 19 python3 -I compare.py "$ROOT"
echo
echo "lddt rows: $(awk '$3=="lddt"' our_afdb_scores.tsv | wc -l), nan rows: $(grep -ci nan our_afdb_scores.tsv)"
# Wall time per run from /usr/bin/time (machine-dependent, not a claim)
for T in foldmason foldmason_fast
do
	cat out/*/$T.time | awk -v t=$T '{s+=$NF; n++} END {printf "%s: %d runs, sum %.1f s, mean %.2f s\n", t, n, s, s/n}'
done
# First and last output written
ls -l --time-style=+%FT%T%z out/*/*.html | awk '{print $6}' | sort | sed -n '1p;$p'
