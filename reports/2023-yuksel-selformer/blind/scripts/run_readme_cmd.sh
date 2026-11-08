#!/bin/bash
# Q3: run the README's binary-classification command, unmodified except --num_epochs,
# which is dropped from 25 to 1 so the run reaches the test block in minutes. The test
# block is the last thing the script does and does not depend on the epoch count.
set -e
BASE=/mnt/e/Ciencia/noturno/2023-yuksel-selformer-cego
export MPLBACKEND=Agg
export OMP_NUM_THREADS=6
export MKL_NUM_THREADS=6
cd "$BASE/repo/SELFormer"
nice -n 19 "$BASE/env/venv-linux/bin/python" train_classification_model.py \
  --model=data/saved_models/SELFormer \
  --tokenizer=data/RobertaFastTokenizer \
  --dataset=data/finetuning_datasets/classification/bbbp/bbbp.csv \
  --save_to="$BASE/tmp/readme_run" \
  --target_column_id=1 \
  --use_scaffold=1 \
  --train_batch_size=16 \
  --validation_batch_size=8 \
  --num_epochs=1 \
  --lr=5e-5 \
  --wd=0
echo "README_CMD_EXIT=$?"
