#!/bin/bash
# Fetch paper, supplement and the authors' per-assay tables at tag PG_v1.3 (read-only, no models)
set -u
cd /mnt/e/Ciencia/pipeline/2023-notin-proteingym/sources
H=cac723e5ff29f65e3fcbb0739ae91bee
P=https://proceedings.neurips.cc/paper_files/paper/2023/file
for f in Paper-Datasets_and_Benchmarks.pdf Supplemental-Datasets_and_Benchmarks.zip Supplemental-Datasets_and_Benchmarks.pdf; do
  curl -sfL -o "neurips_$f" "$P/$H-$f" && echo "ok $f" || { echo "miss $f"; rm -f "neurips_$f"; }
done
curl -sfL -A "Mozilla/5.0" -o biorxiv_570727v1.pdf https://www.biorxiv.org/content/10.1101/2023.12.07.570727v1.full.pdf && echo ok biorxiv || echo miss biorxiv
R=https://raw.githubusercontent.com/OATML-Markslab/ProteinGym/PG_v1.3
mkdir -p repo_PG_v1.3
for f in reference_files/DMS_substitutions.csv \
  benchmarks/DMS_zero_shot/substitutions/Spearman/DMS_substitutions_Spearman_DMS_level.csv \
  benchmarks/DMS_zero_shot/substitutions/Spearman/Summary_performance_DMS_substitutions_Spearman.csv \
  benchmarks/DMS_zero_shot/substitutions/Spearman/DMS_substitutions_Spearman_Uniprot_level.csv \
  benchmarks/DMS_zero_shot/substitutions/Spearman/DMS_substitutions_Spearman_Uniprot_Selection_Type_level.csv \
  proteingym/performance_DMS_benchmarks.py \
  scripts/scoring_DMS_zero_shot/scoring_ESM1b_substitutions.sh \
  scripts/scoring_DMS_zero_shot/scoring_ESM2_substitutions.sh \
  proteingym/baselines/esm/compute_fitness.py; do
  mkdir -p "repo_PG_v1.3/$(dirname $f)"
  curl -sfL -o "repo_PG_v1.3/$f" "$R/$f" && echo "ok $f" || echo "miss $f"
done
git ls-remote https://github.com/OATML-Markslab/ProteinGym PG_v1.3 'refs/tags/*' | head -20
ls -la . repo_PG_v1.3
