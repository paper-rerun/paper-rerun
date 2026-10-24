#!/bin/bash
set -e
source /mnt/e/Ciencia/pipeline/2023-notin-proteingym/env/activate.sh
cd /mnt/e/Ciencia/pipeline/2023-notin-proteingym/exec/B0_testset
git -C /mnt/e/Ciencia/pipeline/2023-notin-proteingym/repo rev-parse HEAD
git -C /mnt/e/Ciencia/pipeline/2023-notin-proteingym/repo status --short reference_files benchmarks
python -I count_testset.py
