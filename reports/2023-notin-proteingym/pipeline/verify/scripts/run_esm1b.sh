#!/bin/bash
# Second attempt at ESM-1b after the import-path fix; waits on the GPU lock behind run_all.sh
W=/mnt/e/Ciencia/pipeline/2023-notin-proteingym
echo "=== esm1b retry $(date -Is)"
bash "$W/verify/scripts/run_scores.sh" esm1b 217 > "$W/verify/logs/scores_esm1b_retry.log" 2>&1 || echo "FAILED esm1b retry"
grep -c '^DONE' "$W/verify/logs/scores_esm1b_retry.log"
echo "=== end $(date -Is)"
