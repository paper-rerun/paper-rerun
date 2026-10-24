#!/bin/bash
# Merge and score with the authors' own merge.py and performance_DMS_benchmarks.py, same flags as merge_all_scores.sh and performance_substitutions.sh
# Changes: --config_file points to a copy of config.json whose substitution model list keeps only the ESM2 size(s) in question,
# because merge.py reads every listed model's score file; and for a sampled size the reference file is the subset of rows we scored
# Usage: post.sh <8M|35M|150M|650M>  -> merge scores/ESM2/<size> into scores/merged_<size>, then the performance script into performance_ours_<size>/
#        post.sh authors              -> performance script straight on authors_merged/ (the zip already holds merged files), 4 sizes, all 217 assays
set -eu
W=/mnt/e/Ciencia/pipeline/2023-notin-proteingym
B=$W/exec/B2_esm2
Tag=$1
source "$W/env/activate.sh"
cd "$B"
python -I - "$W/repo/config.json" "$Tag" "$W/repo/reference_files/DMS_substitutions.csv" <<'PY'
import json, os, sys
import pandas as pd
Config = json.load(open(sys.argv[1]))
Tag = sys.argv[2]
Keys = ["ESM2_8M", "ESM2_35M", "ESM2_150M", "ESM2_650M"] if Tag == "authors" else ["ESM2_" + Tag]
Config["model_list_zero_shot_substitutions_DMS"] = {Key: Config["model_list_zero_shot_substitutions_DMS"][Key] for Key in Keys}
json.dump(Config, open(f"config_{Tag}.json", "w"), indent=1)
Reference = pd.read_csv(sys.argv[3])
if Tag != "authors":
	Reference = Reference[[os.path.exists(f"scores/ESM2/{Tag}/{DmsId}.csv") for DmsId in Reference.DMS_id]]
Reference.to_csv(f"reference_{Tag}.csv", index=False)
print("assays:", len(Reference))
PY
cd "$W/repo/scripts/scoring_DMS_zero_shot"
rm -rf "$B/performance_$Tag"
if [ "$Tag" != "authors" ]; then
	rm -rf "$B/scores/merged_$Tag"
	python ../../proteingym/merge.py \
		--DMS_assays_location "$W/data/DMS_ProteinGym_substitutions/" \
		--model_scores_location "$B/scores" \
		--merged_scores_dir "merged_$Tag" \
		--mutation_type substitutions \
		--DMS_reference_file "$B/reference_$Tag.csv" \
		--config_file "$B/config_$Tag.json" > "$B/logs/merge_$Tag.log" 2>&1
	grep -i -E "warning|skipping" "$B/logs/merge_$Tag.log" || true
	Input=$B/scores/merged_$Tag
else
	Input=$B/authors_merged
fi
python ../../proteingym/performance_DMS_benchmarks.py \
	--input_scoring_files_folder "$Input" \
	--output_performance_file_folder "$B/performance_$Tag" \
	--DMS_reference_file_path "$B/reference_$Tag.csv" \
	--DMS_data_folder "$W/data/DMS_ProteinGym_substitutions/" \
	--performance_by_depth \
	--config_file "$B/config_$Tag.json" > "$B/logs/performance_$Tag.log" 2>&1 \
	|| echo "performance script stopped with an error (a subset can lack an MSA-depth or taxon group the summary needs); the Spearman DMS-level CSV is written before that point"
echo "missing files: $(grep -c 'missing' "$B/logs/performance_$Tag.log" || true)"
cut -d, -f1-5 "$B/performance_$Tag/Spearman/Summary_performance_DMS_substitutions_Spearman.csv" 2>/dev/null || true
