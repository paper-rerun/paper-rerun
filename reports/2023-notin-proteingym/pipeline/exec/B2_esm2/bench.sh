#!/bin/bash
cd /mnt/e/Ciencia/pipeline/2023-notin-proteingym/exec/B2_esm2
flock /mnt/e/Ciencia/.gpu.lock ./py.sh bench.py esm2_t6_8M_UR50D esm2_t12_35M_UR50D esm2_t30_150M_UR50D esm2_t33_650M_UR50D > logs/bench.log 2>&1
