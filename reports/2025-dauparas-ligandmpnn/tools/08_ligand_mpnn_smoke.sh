#!/bin/bash
# Second smoke test: the ligand_mpnn path, which is the one the claims actually
# use. Same shape as the authors' examples (1BC8 plus the ligand checkpoint),
# weights and output redirected so the clone stays clean.
set -euo pipefail

ROOT=/mnt/e/Ciencia/pipeline/2025-dauparas-ligandmpnn
source "$ROOT/env/activate.sh"

OUT=$ROOT/logs/smoke_ligand_mpnn
mkdir -p "$OUT"

flock /mnt/e/Ciencia/.gpu.lock python run.py \
	--model_type "ligand_mpnn" \
	--seed 111 \
	--pdb_path "./inputs/1BC8.pdb" \
	--checkpoint_ligand_mpnn "$LIGANDMPNN_WEIGHTS/ligandmpnn_v_32_010_25.pt" \
	--ligand_mpnn_use_atom_context 1 \
	--ligand_mpnn_use_side_chain_context 0 \
	--temperature 0.1 \
	--batch_size 2 \
	--number_of_batches 5 \
	--out_folder "$OUT"

echo "--- fasta ---"
cat "$OUT"/seqs/*.fa
