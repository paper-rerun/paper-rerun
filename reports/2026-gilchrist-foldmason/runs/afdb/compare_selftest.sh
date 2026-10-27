#!/bin/bash
# Self-test of compare.py: feed the authors' own scores as "ours", every complete-cluster diff must be 0
ROOT=/mnt/e/Ciencia/noturno/2026-gilchrist-foldmason
cd "$ROOT/runs/afdb"
nice -n 19 python3 -I compare.py "$ROOT" "$ROOT/sources/analysis/data/afdb_scores.tsv"
# The per-cluster file from a self-test is not a result
rm -f "$ROOT/runs/afdb/per_cluster_diff.tsv"
