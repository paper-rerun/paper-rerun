#!/usr/bin/env bash
# Block until both design runs for a flavor are complete, up to ~9 minutes per call.
# Usage: wait.sh [flavor]
F=${1:-biounit1}
S=/mnt/e/Ciencia/pipeline/2025-dauparas-ligandmpnn/exec/B3-metal-split/out
for i in $(seq 1 18); do
	l=$(ls "$S/lmpnn_$F/stats" 2>/dev/null | wc -l)
	p=$(ls "$S/pmpnn_$F/stats" 2>/dev/null | wc -l)
	if [ "$l" = "83" ] && [ "$p" = "83" ]; then break; fi
	sleep 30
done
echo "$F lmpnn=$(ls "$S/lmpnn_$F/stats" 2>/dev/null | wc -l) pmpnn=$(ls "$S/pmpnn_$F/stats" 2>/dev/null | wc -l)"
