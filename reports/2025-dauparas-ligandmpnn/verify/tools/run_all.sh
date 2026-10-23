#!/bin/bash
# Every design run for the six claims, one after another under the GPU lock.
# Seeds are fixed here and recorded in each run's log, because run.py draws a
# random one when --seed is 0 (its default) and the paper reports no seed at all.
set -euo pipefail

V=/mnt/e/Ciencia/pipeline/2025-dauparas-ligandmpnn/verify

mkdir -p "$V/inputs/fixed/asym"
cp -f "$V/inputs/fixed/5l70_asym.pdb" "$V/inputs/fixed/asym/5l70.pdb"
cd /tmp
"$V/env/bin/python" -I "$V/tools/make_inputs.py"

bash "$V/tools/run_split.sh" ligand_mpnn  small_molecule 101
bash "$V/tools/run_split.sh" protein_mpnn small_molecule 201
bash "$V/tools/run_split.sh" ligand_mpnn  nucleotide     102
bash "$V/tools/run_split.sh" protein_mpnn nucleotide     202
bash "$V/tools/run_split.sh" ligand_mpnn  metal          103
bash "$V/tools/run_split.sh" protein_mpnn metal          203

echo "ALL RUNS DONE"
