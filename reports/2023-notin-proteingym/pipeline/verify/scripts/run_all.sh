#!/bin/bash
# ESM-1b, 8M, 35M and 150M on all 217 assays; 650M on the first 54 of the fixed-seed order (GPU budget)
W=/mnt/e/Ciencia/pipeline/2023-notin-proteingym
for Pair in "esm1b 217" "8M 217" "35M 217" "150M 217" "650M 54"; do
	set -- $Pair
	echo "=== $1 $2 $(date -Is)"
	bash "$W/verify/scripts/run_scores.sh" "$1" "$2" > "$W/verify/logs/scores_$1.log" 2>&1 || echo "FAILED $1, see logs/scores_$1.log"
	grep -c '^DONE' "$W/verify/logs/scores_$1.log"
done
echo "=== end $(date -Is)"
