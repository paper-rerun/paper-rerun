#!/bin/bash
# Run a python file of this folder inside the frozen env
source /mnt/e/Ciencia/pipeline/2023-notin-proteingym/env/activate.sh
cd /mnt/e/Ciencia/pipeline/2023-notin-proteingym/exec/B2_esm2
python -I "$@"
