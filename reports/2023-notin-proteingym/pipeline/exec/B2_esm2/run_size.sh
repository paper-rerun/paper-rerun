#!/bin/bash
# Score assays with the authors' ESM2 script (masked-marginals, optimal window), one assay per call, through run_authors_script.sh
# Restartable: an assay whose score file already exists is skipped. Per-assay timing goes to timing.tsv
# Usage: run_size.sh <8M|35M|150M|650M> <dms_index>...
set -u
W=/mnt/e/Ciencia/pipeline/2023-notin-proteingym
B=$W/exec/B2_esm2
Out=$B/scores
Size=$1
shift
mkdir -p "$Out/ESM2/$Size" "$B/logs/$Size"
for DmsIndex in "$@"; do
	# Row DmsIndex+2 of the reference file (header is line 1), DMS_id is column 2
	DmsId=$(sed -n "$((DmsIndex + 2))p" "$W/repo/reference_files/DMS_substitutions.csv" | cut -d, -f2)
	if [ -f "$Out/ESM2/$Size/$DmsId.csv" ]; then
		continue
	fi
	Start=$(date +%s)
	if "$W/run_authors_script.sh" "$Size" "$DmsIndex" "$Out" > "$B/logs/$Size/$DmsIndex.log" 2>&1; then
		Status=ok
	else
		Status=FAIL
	fi
	echo -e "$Size\t$DmsIndex\t$DmsId\t$Status\t$(( $(date +%s) - Start ))\t$(date +%H:%M)" >> "$B/timing.tsv"
done
