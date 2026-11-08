#!/bin/bash
# Score every published fine-tuned classification model on its rebuilt scaffold test split.
# CPU only, 6 threads, nice 19.
set -eu
B=/mnt/e/Ciencia/noturno/2023-yuksel-selformer
PY=$B/env/.venv/bin/python
REPO=$B/repo
M=$B/data/extracted/classification_models
OUT=$B/runs/out
LOG=$B/runs/logs
export OMP_NUM_THREADS=6 MKL_NUM_THREADS=6 OPENBLAS_NUM_THREADS=6
export MPLBACKEND=Agg TOKENIZERS_PARALLELISM=false WANDB_DISABLED=true
export CUDA_VISIBLE_DEVICES=""
mkdir -p "$OUT" "$LOG"
cd "$REPO"

run_binary() {
	task=$1; csv=$2; model=$3; split=$4
	echo "--- $task $split"
	nice -n 19 /usr/bin/time -v "$PY" -u "$B/scripts/evaluate_binary.py" \
		--repo "$REPO" --task "$task" --dataset "$csv" --model "$model" \
		--tokenizer "$REPO/data/RobertaFastTokenizer" --target_column_id 1 \
		--split "$split" --device cpu --batch_size 32 \
		--out "$OUT/${task}_${split}.csv" 2>&1 | tee "$LOG/eval_${task}_${split}.log"
}

run_multi() {
	task=$1; csv=$2; model=$3; split=$4
	echo "--- $task $split"
	nice -n 19 /usr/bin/time -v "$PY" -u "$B/scripts/evaluate_multilabel.py" \
		--repo "$REPO" --task "$task" --dataset "$csv" --model "$model" \
		--split "$split" --use_cuda 0 \
		--out "$OUT/${task}_${split}.csv" 2>&1 | tee "$LOG/eval_${task}_${split}.log"
}

case "${1:-all}" in
bbbp)  run_binary bbbp  "$REPO/data/finetuning_datasets/classification/bbbp/bbbp.csv"  "$M/SELFormer_bbbp_scaffold_optimized" "${2:-test}" ;;
bace)  run_binary bace  "$REPO/data/finetuning_datasets/classification/bace/bace.csv"  "$M/SELFormer_bace_scaffold_optimized" "${2:-test}" ;;
tox21) run_multi  tox21 "$REPO/data/finetuning_datasets/classification/tox21/tox21.csv" "$M/SELFormer_tox21_scaffold_optimized" "${2:-test}" ;;
sider) run_multi  sider "$REPO/data/finetuning_datasets/classification/sider/sider.csv" "$M/SELFormer_sider_scaffold_optimized" "${2:-test}" ;;
all)
	bash "$0" bbbp test
	bash "$0" bace test
	bash "$0" sider test
	bash "$0" tox21 test
	;;
esac
