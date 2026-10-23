#!/bin/bash
# The four claim runs left after run_all.sh aborted (editing run_split.sh while
# bash was still reading it killed the loop), then two extra analyses.
#
# The extras test one explanation for the small-molecule gap: our median came out
# about 2 pp above the paper's with the 0.1 A-noise checkpoints the Methods
# describes, and 2 pp is the size the paper itself gives for one noise step
# ("Training with 0.05 A and 0.2 A noise instead increased and decreased sequence
# recovery by about 2%"). So run the 0.2 A checkpoints too, which are also what
# run.py defaults to. Extra analysis only - it cannot change a verdict.
set -euo pipefail

T=/mnt/e/Ciencia/pipeline/2025-dauparas-ligandmpnn/verify/tools

bash "$T/run_split.sh" ligand_mpnn  nucleotide 102
bash "$T/run_split.sh" protein_mpnn nucleotide 202
bash "$T/run_split.sh" ligand_mpnn  metal      103
bash "$T/run_split.sh" protein_mpnn metal      203

echo "CLAIM RUNS DONE"

bash "$T/run_split.sh" ligand_mpnn  small_molecule 101 ligandmpnn_v_32_020_25.pt _noise020
bash "$T/run_split.sh" protein_mpnn small_molecule 201 proteinmpnn_v_48_020.pt    _noise020

echo "ALL RUNS DONE"
