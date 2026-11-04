#!/bin/bash
source /mnt/e/Ciencia/noturno/2023-abbott-gwtc3-population/env/activate.sh
source /mnt/e/Ciencia/noturno/2023-abbott-gwtc3-population/runs/pp_args.sh
python /mnt/e/Ciencia/noturno/2023-abbott-gwtc3-population/runs/check_selection_column.py "${PP_ARGS[@]}" 2>&1 | grep -v "bilby INFO"
