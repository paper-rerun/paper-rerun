#!/bin/bash
# Fetch the authors' per-assay and summary tables for the other Table 2 metrics at PG_v1.3 (CSV only)
set -u
cd /mnt/e/Ciencia/pipeline/2023-notin-proteingym/sources
R=https://raw.githubusercontent.com/OATML-Markslab/ProteinGym/PG_v1.3
for m in AUC MCC NDCG Top_recall; do
  d=benchmarks/DMS_zero_shot/substitutions/$m
  mkdir -p repo_PG_v1.3/$d
  for f in DMS_substitutions_${m}_DMS_level.csv Summary_performance_DMS_substitutions_${m}.csv; do
    curl -sfL -o "repo_PG_v1.3/$d/$f" "$R/$d/$f" && echo "ok $d/$f" || { echo "miss $d/$f"; rm -f "repo_PG_v1.3/$d/$f"; }
  done
done
