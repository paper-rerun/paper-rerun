#!/bin/bash
set -e
source /mnt/e/Ciencia/pipeline/2025-dauparas-ligandmpnn/env/activate.sh
cd /mnt/e/Ciencia/pipeline/2025-dauparas-ligandmpnn/repo
time flock /mnt/e/Ciencia/.gpu.lock python run.py \
  --model_type ligand_mpnn \
  --checkpoint_ligand_mpnn /mnt/e/Ciencia/pipeline/2025-dauparas-ligandmpnn/data/model_params/ligandmpnn_v_32_010_25.pt \
  --pdb_path_multi /mnt/e/Ciencia/pipeline/2025-dauparas-ligandmpnn/exec/B1-small-molecule-split/pdb_list_smoke.json \
  --out_folder /mnt/e/Ciencia/pipeline/2025-dauparas-ligandmpnn/exec/B1-small-molecule-split/smoke_lmpnn \
  --batch_size 10 --number_of_batches 1 \
  --temperature 0.1 \
  --ligand_mpnn_use_atom_context 1 \
  --ligand_mpnn_use_side_chain_context 0 \
  --parse_atoms_with_zero_occupancy 0 \
  --seed 20251022 \
  --save_stats 1 \
  --verbose 0
