#!/usr/bin/env bash
set -euo pipefail
ROOT=/mnt/e/Ciencia/pipeline/2025-dauparas-ligandmpnn
source "$ROOT/env/activate.sh"
time flock /mnt/e/Ciencia/.gpu.lock python run.py \
	--model_type ligand_mpnn \
	--checkpoint_ligand_mpnn "$ROOT/data/model_params/ligandmpnn_v_32_010_25.pt" \
	--pdb_path "$ROOT/data/structures/biounit1/5i4j.pdb" \
	--out_folder "$ROOT/exec/B3-metal-split/trial" \
	--batch_size 10 --number_of_batches 1 --temperature 0.1 --seed 37 --save_stats 1
