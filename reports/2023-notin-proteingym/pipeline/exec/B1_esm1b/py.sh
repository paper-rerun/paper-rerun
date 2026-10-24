#!/bin/bash
# Run a python file of this folder inside the frozen env
source /mnt/e/Ciencia/pipeline/2023-notin-proteingym/env/activate.sh
python -I "$@"
