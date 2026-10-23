#!/bin/bash
# LigandMPNN with the 0.2 A-noise checkpoint on the nucleotide and metal splits.
#
# On the small-molecule split that checkpoint reproduces the authors' per-protein
# LigandMPNN values with a bias of -0.06 pp, against +2.25 pp for the 0.1 A
# checkpoint the Methods describes. So test the same thing on the other two
# splits, under both input readings (whole deposited file, and protein + the
# class that names the split).
set -euo pipefail

T=/mnt/e/Ciencia/pipeline/2025-dauparas-ligandmpnn/verify/tools
C=ligandmpnn_v_32_020_25.pt

bash "$T/run_split.sh" ligand_mpnn metal                103 "$C" _noise020
bash "$T/run_split.sh" ligand_mpnn metal_classonly      103 "$C" _noise020
bash "$T/run_split.sh" ligand_mpnn nucleotide           102 "$C" _noise020
bash "$T/run_split.sh" ligand_mpnn nucleotide_classonly 102 "$C" _noise020

echo "NOISE020 RUNS DONE"
