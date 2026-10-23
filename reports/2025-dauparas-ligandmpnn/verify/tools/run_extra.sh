#!/bin/bash
# Extra analysis: LigandMPNN on inputs whose context is only the class that names
# the split (protein + nucleic acid, protein + transition metal). Same seeds as
# the claim runs, so the input is the only thing that changed.
#
# ProteinMPNN is not re-run: with --model_type protein_mpnn the context atoms
# never enter the features, so its designed sequences do not depend on them. The
# existing ProteinMPNN runs are re-scored against the new masks instead.
set -euo pipefail

T=/mnt/e/Ciencia/pipeline/2025-dauparas-ligandmpnn/verify/tools

bash "$T/run_split.sh" ligand_mpnn nucleotide_classonly 102
bash "$T/run_split.sh" ligand_mpnn metal_classonly      103

echo "EXTRA RUNS DONE"
