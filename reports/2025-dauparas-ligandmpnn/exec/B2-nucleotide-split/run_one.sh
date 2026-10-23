#!/bin/bash
# One resumable pass of one model over the ids that still have no stats file.
#   usage: run_one.sh <lmpnn|pmpnn> <biounit1|asym>
#
# Fixed before running, per the claim definitions:
#   10 sequences  = batch_size 1 x number_of_batches 10
#   temperature   = 0.1 (released default)
#   seeds         = 20251022 LigandMPNN, 20251023 ProteinMPNN
#   checkpoints   = ligandmpnn_v_32_010_25.pt and proteinmpnn_v_48_010.pt (0.1 A noise)
#   whole protein redesigned: no fixed residues, no bias, no omitted amino acids
#   main input    = biological assembly 1; asym is an extra analysis run afterwards
set -euo pipefail

ROOT=/mnt/e/Ciencia/pipeline/2025-dauparas-ligandmpnn
BLOCK=$ROOT/exec/B2-nucleotide-split
MODEL=$1
FLAVOR=$2
OUTDIR=$BLOCK/${MODEL}_${FLAVOR}
LIST=$BLOCK/todo_${MODEL}_${FLAVOR}.json

source "$ROOT/env/activate.sh"
mkdir -p "$OUTDIR"

python "$BLOCK/make_multi.py" "$FLAVOR" "$OUTDIR" "$LIST"

if [ "$(python -c "import json,sys;print(len(json.load(open(sys.argv[1]))))" "$LIST")" = "0" ]; then
	echo "NOTHING TO DO ${MODEL}_${FLAVOR}"
	exit 0
fi

if [ "$MODEL" = "lmpnn" ]; then
	flock /mnt/e/Ciencia/.gpu.lock python run.py \
		--model_type "ligand_mpnn" \
		--checkpoint_ligand_mpnn "$LIGANDMPNN_WEIGHTS/ligandmpnn_v_32_010_25.pt" \
		--ligand_mpnn_use_atom_context 1 \
		--ligand_mpnn_use_side_chain_context 0 \
		--temperature 0.1 --batch_size 1 --number_of_batches 10 \
		--seed 20251022 --save_stats 1 --verbose 0 \
		--pdb_path_multi "$LIST" --out_folder "$OUTDIR"
else
	flock /mnt/e/Ciencia/.gpu.lock python run.py \
		--model_type "protein_mpnn" \
		--checkpoint_protein_mpnn "$LIGANDMPNN_WEIGHTS/proteinmpnn_v_48_010.pt" \
		--temperature 0.1 --batch_size 1 --number_of_batches 10 \
		--seed 20251023 --save_stats 1 --verbose 0 \
		--pdb_path_multi "$LIST" --out_folder "$OUTDIR"
fi

echo "PASS DONE ${MODEL}_${FLAVOR} stats=$(ls "$OUTDIR/stats" | wc -l)"
