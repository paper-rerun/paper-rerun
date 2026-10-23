#!/usr/bin/env bash
# B3-metal-split: design 10 sequences per protein for the 83 metal-split entries,
# with LigandMPNN and with the retrained ProteinMPNN. Fixed readings, recorded here:
#   structure file = biological assembly 1 (the Results say "PDB biounits")
#   full redesign, T=0.1, batch_size 10 x 1 batch, side-chain context off
#   seed 37 for LigandMPNN, 38 for ProteinMPNN
# Usage: run_block.sh <flavor>   (flavor = biounit1 | asym)
set -euo pipefail

ROOT=/mnt/e/Ciencia/pipeline/2025-dauparas-ligandmpnn
EXEC=$ROOT/exec/B3-metal-split
FLAVOR=${1:-biounit1}

source "$ROOT/env/activate.sh"

flock /mnt/e/Ciencia/.gpu.lock python run.py \
	--model_type ligand_mpnn \
	--checkpoint_ligand_mpnn "$ROOT/data/model_params/ligandmpnn_v_32_010_25.pt" \
	--pdb_path_multi "$EXEC/pdb_multi_$FLAVOR.json" \
	--out_folder "$EXEC/out/lmpnn_$FLAVOR" \
	--batch_size 10 --number_of_batches 1 \
	--temperature 0.1 --seed 37 \
	--ligand_mpnn_use_atom_context 1 \
	--ligand_mpnn_use_side_chain_context 0 \
	--save_stats 1 --verbose 0

flock /mnt/e/Ciencia/.gpu.lock python run.py \
	--model_type protein_mpnn \
	--checkpoint_protein_mpnn "$ROOT/data/model_params/proteinmpnn_v_48_010.pt" \
	--pdb_path_multi "$EXEC/pdb_multi_$FLAVOR.json" \
	--out_folder "$EXEC/out/pmpnn_$FLAVOR" \
	--batch_size 10 --number_of_batches 1 \
	--temperature 0.1 --seed 38 \
	--save_stats 1 --verbose 0

echo "DONE $FLAVOR"
