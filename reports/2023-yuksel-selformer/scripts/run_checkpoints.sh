#!/bin/bash
# Both model folders also ship the last epoch's checkpoint next to the saved model.
# Score the test split with those too, to see whether the table's number sits there.
set -eu
B=/mnt/e/Ciencia/noturno/2023-yuksel-selformer
PY=$B/env/.venv/bin/python
REPO=$B/repo
M=$B/data/extracted/classification_models
export OMP_NUM_THREADS=6 MKL_NUM_THREADS=6 OPENBLAS_NUM_THREADS=6
export MPLBACKEND=Agg TOKENIZERS_PARALLELISM=false WANDB_DISABLED=true CUDA_VISIBLE_DEVICES=""
cd "$REPO"

score() {
	task=$1; csv=$2; model=$3; tag=$4
	nice -n 19 "$PY" -u "$B/scripts/evaluate_binary.py" --repo "$REPO" --task "${task}_${tag}" \
		--dataset "$csv" --model "$model" --tokenizer "$REPO/data/RobertaFastTokenizer" \
		--target_column_id 1 --split test --device cpu --batch_size 32 \
		--out "$B/runs/out/${task}_test_${tag}.csv" 2>&1 | tee "$B/runs/logs/eval_${task}_test_${tag}.log"
}

score bbbp "$REPO/data/finetuning_datasets/classification/bbbp/bbbp.csv" \
	"$M/SELFormer_bbbp_scaffold_optimized/checkpoint-10200" ckpt10200
score bace "$REPO/data/finetuning_datasets/classification/bace/bace.csv" \
	"$M/SELFormer_bace_scaffold_optimized/checkpoint-1900" ckpt1900
