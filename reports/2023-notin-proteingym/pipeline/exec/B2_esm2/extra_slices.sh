#!/bin/bash
# Usage: extra_slices.sh <size> <checkpoint> <DMS_id>... ; scores the full target_seq and its MSA region for each assay
cd /mnt/e/Ciencia/pipeline/2023-notin-proteingym/exec/B2_esm2
Size=$1
Checkpoint=$2
shift 2
for DmsId in "$@"; do
	flock /mnt/e/Ciencia/.gpu.lock ./py.sh extra_slices.py "$Size" "$Checkpoint" "$DmsId" msa > "logs/extra_slices_${Size}_$DmsId.log" 2>&1
	grep -v -i warn "logs/extra_slices_${Size}_$DmsId.log" | tail -n 2
done
