#!/bin/bash
# Merge and score with the authors' own merge.py and performance_DMS_benchmarks.py, same flags as merge_all_scores.sh and performance_substitutions.sh
# Only change: --config_file points to a copy of config.json whose substitution model list keeps only ESM1b, because merge.py reads every listed model's score file
# Usage: post.sh ours     -> merge scores/ESM1b into scores/merged_ours, then the performance script into performance_ours/
#        post.sh authors  -> performance script straight on authors_merged/ (the zip already holds merged files) into performance_authors/
set -eu
W=/mnt/e/Ciencia/pipeline/2023-notin-proteingym
B=$W/exec/B1_esm1b
Tag=$1
source "$W/env/activate.sh"
python -I - "$W/repo/config.json" "$B/config_ESM1b_only.json" <<'PY'
import json, sys
Config = json.load(open(sys.argv[1]))
Config["model_list_zero_shot_substitutions_DMS"] = {"ESM1b": Config["model_list_zero_shot_substitutions_DMS"]["ESM1b"]}
json.dump(Config, open(sys.argv[2], "w"), indent=1)
PY
cd "$W/repo/scripts/scoring_DMS_zero_shot"
rm -rf "$B/performance_$Tag"
if [ "$Tag" = "ours" ]; then
	rm -rf "$B/scores/merged_ours"
	python ../../proteingym/merge.py \
		--DMS_assays_location "$W/data/DMS_ProteinGym_substitutions/" \
		--model_scores_location "$B/scores" \
		--merged_scores_dir merged_ours \
		--mutation_type substitutions \
		--config_file "$B/config_ESM1b_only.json" > "$B/logs/merge_ours.log" 2>&1
	grep -i -E "warning|skipping" "$B/logs/merge_ours.log" || true
	Input=$B/scores/merged_ours
else
	Input=$B/authors_merged
fi
python ../../proteingym/performance_DMS_benchmarks.py \
	--input_scoring_files_folder "$Input" \
	--output_performance_file_folder "$B/performance_$Tag" \
	--DMS_reference_file_path ../../reference_files/DMS_substitutions.csv \
	--DMS_data_folder "$W/data/DMS_ProteinGym_substitutions/" \
	--performance_by_depth \
	--config_file "$B/config_ESM1b_only.json" > "$B/logs/performance_$Tag.log" 2>&1
echo "missing files: $(grep -c 'missing' "$B/logs/performance_$Tag.log" || true)"
cut -d, -f1-5 "$B/performance_$Tag/Spearman/Summary_performance_DMS_substitutions_Spearman.csv"
