#!/bin/bash
# Which aggregation reproduces the paper numbers from the authors' own per-assay Spearman CSVs
W=/mnt/e/Ciencia/meio/2023-notin-proteingym
P=$W/env/.venv/bin/python
for V in 1.0 1.1 1.3; do
	echo "== PG_v$V"
	$P $W/runs/aggregate.py $W/sources/repo_csv/DMS_level_PG_v$V.csv $W/sources/repo_csv/DMS_substitutions_PG_v$V.csv "ESM-1b" "ESM2 (8M)" "ESM2 (35M)" "ESM2 (150M)" "ESM2 (650M)"
done
