#!/bin/bash
# Self-consistency check: score the VALIDATION fold with the released checkpoint and
# compare against eval_roc-auc / eval_accuracy recorded in its own trainer_state.json.
# $1 = task (bace|bbbp), $2 = eval batch size (default 8)
set -e
BASE=/mnt/e/Ciencia/noturno/2023-yuksel-selformer-cego
PY="$BASE/env/venv-linux/bin/python"
REPO="$BASE/repo/SELFormer"
MODELS="$BASE/downloads/models/classification_models"
export MPLBACKEND=Agg
export OMP_NUM_THREADS=6
export MKL_NUM_THREADS=6
export TOKENIZERS_PARALLELISM=false
TASK="$1"
BS="${2:-8}"
nice -n 19 "$PY" "$BASE/scripts/eval_binary.py" \
  --repo "$REPO" \
  --model "$MODELS/SELFormer_${TASK}_scaffold_optimized" \
  --tokenizer "$REPO/data/RobertaFastTokenizer" \
  --dataset "$REPO/data/finetuning_datasets/classification/$TASK/$TASK.csv" \
  --target_column_id 1 \
  --eval_batch_size "$BS" \
  --fold val \
  --tmp "$BASE/tmp/$TASK" \
  --out "$BASE/results/${TASK}_valfold_bs${BS}.json"
echo "SELFCHECK_DONE $TASK bs=$BS"
