#!/bin/bash
source /mnt/e/Ciencia/pipeline/2025-ko-matgl/env/activate.sh
cd /mnt/e/Ciencia/pipeline/2025-ko-matgl/exec/data-description
python -I count_animd.py 2>&1 | tee run.log
