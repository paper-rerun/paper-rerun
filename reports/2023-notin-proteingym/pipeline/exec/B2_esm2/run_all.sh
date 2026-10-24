#!/bin/bash
# Whole schedule: the 30 sampled assays for every size first, so each claim gets per-assay data early, then the rest of 8M
set -u
B=/mnt/e/Ciencia/pipeline/2023-notin-proteingym/exec/B2_esm2
Sample=$(python3 -c "import json; print(' '.join(map(str, json.load(open('$B/sample.json'))['35M'])))")
for Size in 8M 35M 150M 650M; do
	"$B/run_size.sh" "$Size" $Sample
done
"$B/run_size.sh" 8M $(seq 0 216)
echo "schedule done $(date)"
