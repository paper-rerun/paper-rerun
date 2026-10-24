#!/bin/bash
# Run the authors' ESM scoring script for one assay, with only the placeholders filled in.
# Usage: run_authors_script.sh <esm1b|8M|35M|150M|650M> <dms_index, 0-based row of DMS_substitutions.csv> <output_root>
# Scores land in <output_root>/ESM1b/<DMS_id>.csv or <output_root>/ESM2/<size>/<DMS_id>.csv
# What changes vs the repo (see patches/authors_script_placeholders.md):
#   - zero_shot_config.sh: PROTEINGYM_CACHE points at data/, score output at <output_root> (so the authors' scores are never overwritten)
#   - "source activate proteingym_env" (conda) becomes our venv
#   - checkpoint path and DMS_index placeholders get real values; for ESM2 the size pair is uncommented, as the script header says
# The GPU part runs under the shared lock
set -eu
W=/mnt/e/Ciencia/pipeline/2023-notin-proteingym
Model=$1
DmsIndex=$2
OutputRoot=$(realpath -m "$3")
ScriptDir=$W/repo/scripts/scoring_DMS_zero_shot
Tmp=$(mktemp -d "$W/runs_tmp.XXXXXX")
trap 'rm -rf "$Tmp"' EXIT

# Config copy: same file, with our data and output folders appended at the end
cp "$W/repo/scripts/zero_shot_config.sh" "$Tmp/zero_shot_config.sh"
cat >> "$Tmp/zero_shot_config.sh" <<CFG
export PROTEINGYM_CACHE="$W/data"
export DMS_data_folder_subs="$W/data/DMS_ProteinGym_substitutions/"
export DMS_output_score_folder_subs="$OutputRoot/"
CFG

if [ "$Model" = "esm1b" ]; then
	Source=$ScriptDir/scoring_ESM1b_substitutions.sh
	Checkpoint=$W/data/weights/esm1b_t33_650M_UR50S.pt
	mkdir -p "$OutputRoot/ESM1b"
	sed -e "s#^source ../zero_shot_config.sh#source $Tmp/zero_shot_config.sh#" \
		-e "s#^source activate proteingym_env#source $W/env/activate.sh#" \
		-e "s#\"path to ESM1b checkpoint\"#\"$Checkpoint\"#" \
		-e "s#\"Experiment index to run (e.g. 1,2,...217)\"#$DmsIndex#" \
		"$Source" > "$Tmp/score.sh"
else
	case "$Model" in
		8M) Name=esm2_t6_8M_UR50D ;;
		35M) Name=esm2_t12_35M_UR50D ;;
		150M) Name=esm2_t30_150M_UR50D ;;
		650M) Name=esm2_t33_650M_UR50D ;;
		*) echo "unknown model $Model"; exit 1 ;;
	esac
	Source=$ScriptDir/scoring_ESM2_substitutions.sh
	Checkpoint=$W/data/weights/$Name.pt
	mkdir -p "$OutputRoot/ESM2/$Model"
	# Comment out the active 8M pair, then uncomment the pair for the chosen size (for 8M this puts it back)
	sed -e "s#^source ../zero_shot_config.sh#source $Tmp/zero_shot_config.sh#" \
		-e "s#^source activate proteingym_env#source $W/env/activate.sh#" \
		-e 's|^export model_checkpoint="path to 8M|# export model_checkpoint="path to 8M|' \
		-e 's|^export dms_output_folder=\(.*\)/ESM2/8M|# export dms_output_folder=\1/ESM2/8M|' \
		-e "s|^# export model_checkpoint=\"path to $Model ESM2 checkpoint\"|export model_checkpoint=\"$Checkpoint\"|" \
		-e "s|^# export dms_output_folder=\(.*\)/ESM2/$Model *\$|export dms_output_folder=\1/ESM2/$Model|" \
		-e "s#\"Experiment index to run (e.g. 1,2,...217)\"#$DmsIndex#" \
		"$Source" > "$Tmp/score.sh"
fi

# Keep a copy of exactly what ran, next to the scores
mkdir -p "$OutputRoot/_scripts"
cp "$Tmp/score.sh" "$OutputRoot/_scripts/${Model}_${DmsIndex}.sh"
cd "$ScriptDir"
export MPLBACKEND=Agg
flock /mnt/e/Ciencia/.gpu.lock bash "$Tmp/score.sh"
