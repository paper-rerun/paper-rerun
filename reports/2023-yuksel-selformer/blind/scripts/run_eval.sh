#!/bin/bash
# Score one released checkpoint. $1 = task name.
set -e
BASE=/mnt/e/Ciencia/noturno/2023-yuksel-selformer-cego
PY="$BASE/env/venv-linux/bin/python"
REPO="$BASE/repo/SELFormer"
MODELS="$BASE/downloads/models/classification_models"
export MPLBACKEND=Agg
export OMP_NUM_THREADS=6
export MKL_NUM_THREADS=6
export TOKENIZERS_PARALLELISM=false
mkdir -p "$BASE/results" "$BASE/logs" "$BASE/tmp"
TASK="$1"
case "$TASK" in
  bace|bbbp|hiv)
    nice -n 19 "$PY" "$BASE/scripts/eval_binary.py" \
      --repo "$REPO" \
      --model "$MODELS/SELFormer_${TASK}_scaffold_optimized" \
      --tokenizer "$REPO/data/RobertaFastTokenizer" \
      --dataset "$REPO/data/finetuning_datasets/classification/$TASK/$TASK.csv" \
      --target_column_id 1 \
      --eval_batch_size 8 \
      --tmp "$BASE/tmp/$TASK" \
      --out "$BASE/results/$TASK.json"
    ;;
  tox21|sider)
    nice -n 19 "$PY" "$BASE/scripts/eval_multilabel.py" \
      --repo "$REPO" \
      --model "$MODELS/SELFormer_${TASK}_scaffold_optimized" \
      --dataset "$REPO/data/finetuning_datasets/classification/$TASK/$TASK.csv" \
      --eval_batch_size 8 \
      --out "$BASE/results/$TASK.json"
    ;;
  *) echo "unknown task $TASK"; exit 2 ;;
esac
echo "EVAL_DONE $TASK"
