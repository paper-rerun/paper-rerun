#!/bin/bash
# Score every variant run that is not scored yet.
set -euo pipefail
P=/mnt/e/Ciencia/pipeline/2025-dauparas-ligandmpnn/verify
cd /tmp
export MPLBACKEND=Agg

S() { "$P/env/bin/python" "$P/tools/score_recovery.py" "$@" > /dev/null 2>&1 && echo "scored: $*"; }

S nucleotide           ligand_mpnn nucleotide_noise020
S nucleotide_classonly ligand_mpnn nucleotide_classonly_noise020
S metal_classonly      ligand_mpnn metal_classonly_noise020
echo "SCORING DONE"
