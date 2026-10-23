#!/bin/bash
# Drives the two models to completion on one flavor. Each pass only designs the ids that
# still have no stats file, so a pass that dies mid-way costs us the current structure,
# not the run. Three passes per model, then it gives up and says so.
#   usage: run_all.sh <biounit1|asym>
set -uo pipefail

BLOCK=/mnt/e/Ciencia/pipeline/2025-dauparas-ligandmpnn/exec/B2-nucleotide-split
FLAVOR=${1:-biounit1}

for MODEL in lmpnn pmpnn; do
	for PASS in 1 2 3; do
		echo "### pass $PASS $MODEL $FLAVOR $(date -Is)"
		bash "$BLOCK/run_one.sh" "$MODEL" "$FLAVOR"
		N=$(ls "$BLOCK/${MODEL}_${FLAVOR}/stats" 2>/dev/null | wc -l)
		echo "### after pass $PASS: $MODEL $FLAVOR stats=$N"
		if [ "$N" = "74" ]; then
			break
		fi
	done
	if [ "$(ls "$BLOCK/${MODEL}_${FLAVOR}/stats" 2>/dev/null | wc -l)" != "74" ]; then
		echo "GAVE UP on $MODEL $FLAVOR after 3 passes"
		exit 1
	fi
done
echo "ALL DONE $FLAVOR"
