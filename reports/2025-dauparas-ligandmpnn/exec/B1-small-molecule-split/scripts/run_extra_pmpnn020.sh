#!/bin/bash
# Extra analysis, not the main result: ProteinMPNN with run.py's own default
# checkpoint, proteinmpnn_v_48_020.pt (0.2 A training noise) instead of the
# 0.1 A one the paper states for the comparison.
set -e
source /mnt/e/Ciencia/pipeline/2025-dauparas-ligandmpnn/env/activate.sh
cd /mnt/e/Ciencia/pipeline/2025-dauparas-ligandmpnn/repo
BASE=/mnt/e/Ciencia/pipeline/2025-dauparas-ligandmpnn/exec/B1-small-molecule-split

echo "=== extra pmpnn 0.2A start $(date -Is)"
flock /mnt/e/Ciencia/.gpu.lock python run.py \
  --model_type protein_mpnn \
  --checkpoint_protein_mpnn /mnt/e/Ciencia/pipeline/2025-dauparas-ligandmpnn/data/model_params/proteinmpnn_v_48_020.pt \
  --pdb_path_multi "$BASE/pdb_list.json" \
  --out_folder "$BASE/out_pmpnn020" \
  --batch_size 5 --number_of_batches 2 \
  --temperature 0.1 \
  --parse_atoms_with_zero_occupancy 0 \
  --seed 20251024 \
  --save_stats 1 \
  --verbose 0
echo "=== extra pmpnn 0.2A done $(date -Is)"
echo "all done"
