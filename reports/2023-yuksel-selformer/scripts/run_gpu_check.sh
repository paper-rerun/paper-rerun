#!/bin/bash
# Same BBBP test split, same weights, on the GPU, to see whether the device moves the number.
# Half the card at most, batch 16, one process at a time.
set -eu
B=/mnt/e/Ciencia/noturno/2023-yuksel-selformer
export OMP_NUM_THREADS=6 MKL_NUM_THREADS=6 MPLBACKEND=Agg TOKENIZERS_PARALLELISM=false WANDB_DISABLED=true
cd "$B/repo"
nice -n 19 "$B/env/.venv/bin/python" -u "$B/scripts/evaluate_binary.py" \
	--repo "$B/repo" --task bbbp_gpu \
	--dataset "$B/repo/data/finetuning_datasets/classification/bbbp/bbbp.csv" \
	--model "$B/data/extracted/classification_models/SELFormer_bbbp_scaffold_optimized" \
	--tokenizer "$B/repo/data/RobertaFastTokenizer" --target_column_id 1 \
	--split test --device cuda --batch_size 16 \
	--out "$B/runs/out/bbbp_test_gpu.csv" 2>&1 | tee "$B/runs/logs/eval_bbbp_test_gpu.log"
