#!/bin/bash
# B2-nucleotide-split: the two designs the claims need (C3 LigandMPNN, C4 ProteinMPNN)
# on the 74 ids of training/test_nucleotide.json.
#
# Fixed before running, per the claim definitions:
#   input file  = biological assembly 1 (data/structures/biounit1/<id>.pdb), because the
#                 Results call the training data "PDB biounits". The asymmetric unit is an
#                 extra analysis, run after, never as the main number.
#   10 sequences = batch_size 1 x number_of_batches 10
#   temperature  = 0.1 (released default)
#   seeds        = 20251022 LigandMPNN, 20251023 ProteinMPNN
#   whole protein redesigned, no fixed residues, no bias, no omitted AAs
set -euo pipefail

ROOT=/mnt/e/Ciencia/pipeline/2025-dauparas-ligandmpnn
OUT=$ROOT/exec/B2-nucleotide-split
FLAVOR=${1:-biounit1}

source "$ROOT/env/activate.sh"

python "$OUT/make_multi.py" "$FLAVOR"

echo "=== LigandMPNN ($FLAVOR) ==="
flock /mnt/e/Ciencia/.gpu.lock python run.py \
	--model_type "ligand_mpnn" \
	--checkpoint_ligand_mpnn "$LIGANDMPNN_WEIGHTS/ligandmpnn_v_32_010_25.pt" \
	--ligand_mpnn_use_atom_context 1 \
	--ligand_mpnn_use_side_chain_context 0 \
	--temperature 0.1 \
	--batch_size 1 \
	--number_of_batches 10 \
	--seed 20251022 \
	--save_stats 1 \
	--pdb_path_multi "$OUT/pdb_multi_$FLAVOR.json" \
	--out_folder "$OUT/lmpnn_$FLAVOR"

echo "=== ProteinMPNN ($FLAVOR) ==="
flock /mnt/e/Ciencia/.gpu.lock python run.py \
	--model_type "protein_mpnn" \
	--checkpoint_protein_mpnn "$LIGANDMPNN_WEIGHTS/proteinmpnn_v_48_010.pt" \
	--temperature 0.1 \
	--batch_size 1 \
	--number_of_batches 10 \
	--seed 20251023 \
	--save_stats 1 \
	--pdb_path_multi "$OUT/pdb_multi_$FLAVOR.json" \
	--out_folder "$OUT/pmpnn_$FLAVOR"

echo "DONE $FLAVOR"
