#!/bin/bash
# Example 1 of the authors' run_examples.sh, unchanged except for two paths:
# weights come from data/model_params and output goes to logs/, so the clone
# stays clean. Runs under the GPU lock.
set -euo pipefail

ROOT=/mnt/e/Ciencia/pipeline/2025-dauparas-ligandmpnn
source "$ROOT/env/activate.sh"

OUT=$ROOT/logs/smoke_default
mkdir -p "$OUT"

flock /mnt/e/Ciencia/.gpu.lock python run.py \
	--seed 111 \
	--pdb_path "./inputs/1BC8.pdb" \
	--checkpoint_protein_mpnn "$LIGANDMPNN_WEIGHTS/proteinmpnn_v_48_020.pt" \
	--out_folder "$OUT"

echo "--- fasta ---"
cat "$OUT"/seqs/*.fa
echo "--- files ---"
find "$OUT" -type f | sort
