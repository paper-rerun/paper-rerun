#!/bin/bash
# B1-small-molecule-split: the two main runs.
# batch_size 5 x number_of_batches 2 = 10 sequences per protein (run.py defaults
# both to 1). Seeds are explicit and non-zero because run.py tests "if args.seed".
set -e
source /mnt/e/Ciencia/pipeline/2025-dauparas-ligandmpnn/env/activate.sh
cd /mnt/e/Ciencia/pipeline/2025-dauparas-ligandmpnn/repo

BASE=/mnt/e/Ciencia/pipeline/2025-dauparas-ligandmpnn/exec/B1-small-molecule-split

echo "=== C1 LigandMPNN start $(date -Is)"
flock /mnt/e/Ciencia/.gpu.lock python run.py \
  --model_type ligand_mpnn \
  --checkpoint_ligand_mpnn /mnt/e/Ciencia/pipeline/2025-dauparas-ligandmpnn/data/model_params/ligandmpnn_v_32_010_25.pt \
  --pdb_path_multi "$BASE/pdb_list.json" \
  --out_folder "$BASE/out_lmpnn" \
  --batch_size 5 --number_of_batches 2 \
  --temperature 0.1 \
  --ligand_mpnn_use_atom_context 1 \
  --ligand_mpnn_use_side_chain_context 0 \
  --parse_atoms_with_zero_occupancy 0 \
  --seed 20251022 \
  --save_stats 1 \
  --verbose 0
echo "=== C1 LigandMPNN done $(date -Is)"

echo "=== C2 ProteinMPNN start $(date -Is)"
flock /mnt/e/Ciencia/.gpu.lock python run.py \
  --model_type protein_mpnn \
  --checkpoint_protein_mpnn /mnt/e/Ciencia/pipeline/2025-dauparas-ligandmpnn/data/model_params/proteinmpnn_v_48_010.pt \
  --pdb_path_multi "$BASE/pdb_list.json" \
  --out_folder "$BASE/out_pmpnn" \
  --batch_size 5 --number_of_batches 2 \
  --temperature 0.1 \
  --parse_atoms_with_zero_occupancy 0 \
  --seed 20251023 \
  --save_stats 1 \
  --verbose 0
echo "=== C2 ProteinMPNN done $(date -Is)"
echo "all done"
