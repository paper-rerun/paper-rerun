#!/bin/bash
# Design every structure of one split with one model.
#
#   bash run_split.sh <ligand_mpnn|protein_mpnn> <small_molecule|nucleotide|metal> <seed>
#
# 5 x 2 rather than 1 x 10 because model_utils.sample() loops over residues in
# Python, so one batch of 5 costs about what one sequence costs; the number of
# sequences per protein is 10 either way, which is what the claim sheet fixes.
# 5 and not 10 to leave headroom on the 8 GB card for the 1,398-residue metal case.
#
# Conditions are the ones fixed in the claim sheet: 10 sequences per protein,
# T = 0.1, whole chain redesigned, nothing fixed, no bias, zero-occupancy atoms
# dropped, explicit non-zero seed. LigandMPNN gets the 0.1 A / 25-atom checkpoint
# and ProteinMPNN the 0.1 A one, which is NOT run.py's own default of 0.2 A.
# --save_stats 1 is what lets the scorer read the designed sequence in the
# parser's own residue order instead of guessing it back out of the fasta.
set -euo pipefail

MODEL=$1
SPLIT=$2
SEED=$3
CKPT=${4:-}            # optional checkpoint override, e.g. ligandmpnn_v_32_020_25.pt
TAG=${5:-}             # optional suffix for the output folder

ROOT=/mnt/e/Ciencia/pipeline/2025-dauparas-ligandmpnn
VROOT=$ROOT/verify
source "$VROOT/env/activate.sh"

OUT=$VROOT/out/${MODEL}_${SPLIT}${TAG}
mkdir -p "$OUT"
PATHS=$VROOT/inputs/${SPLIT}_paths.json

COMMON=(
	--pdb_path_multi "$PATHS"
	--out_folder "$OUT"
	--seed "$SEED"
	--temperature 0.1
	--batch_size 5
	--number_of_batches 2
	--parse_atoms_with_zero_occupancy 0
	--save_stats 1
	--verbose 0
)

if [ "$MODEL" = "ligand_mpnn" ]; then
	EXTRA=(
		--model_type ligand_mpnn
		--checkpoint_ligand_mpnn "$LIGANDMPNN_WEIGHTS/${CKPT:-ligandmpnn_v_32_010_25.pt}"
		--ligand_mpnn_use_atom_context 1
		--ligand_mpnn_use_side_chain_context 0
	)
else
	EXTRA=(
		--model_type protein_mpnn
		--checkpoint_protein_mpnn "$LIGANDMPNN_WEIGHTS/${CKPT:-proteinmpnn_v_48_010.pt}"
	)
fi

echo "=== $MODEL / $SPLIT${TAG} / seed $SEED / ckpt ${CKPT:-default-for-claims} ==="
date -Is
flock /mnt/e/Ciencia/.gpu.lock python run.py "${COMMON[@]}" "${EXTRA[@]}"
date -Is
echo "stats files: $(ls "$OUT/stats" | wc -l)"
