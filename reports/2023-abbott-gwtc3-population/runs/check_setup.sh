#!/bin/bash
set -e
source /mnt/e/Ciencia/noturno/2023-abbott-gwtc3-population/env/activate.sh
B=/mnt/e/Ciencia/noturno/2023-abbott-gwtc3-population
source $B/runs/pp_args.sh
RUN=$B/runs/check_setup
mkdir -p $RUN
[ -f $RUN/data/posteriors.pkl ] || python $B/runs/prep_data.py $RUN
python $B/runs/check_setup.py $RUN "${PP_ARGS[@]}" --run-dir $RUN
