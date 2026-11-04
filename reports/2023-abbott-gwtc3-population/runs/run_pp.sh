#!/bin/bash
# Usage: run_pp.sh <seed>   (restartable: bilby resumes from the dynesty checkpoint in <run_dir>/result)
set -e
source /mnt/e/Ciencia/noturno/2023-abbott-gwtc3-population/env/activate.sh
B=/mnt/e/Ciencia/noturno/2023-abbott-gwtc3-population
source $B/runs/pp_args.sh
SEED=$1
RUN=$B/runs/pp_seed$SEED
mkdir -p $RUN
[ -f $RUN/data/posteriors.pkl ] || python $B/runs/prep_data.py $RUN
cd $RUN
python -u $B/runs/run_pp.py $SEED "${PP_ARGS[@]}" --run-dir $RUN
echo RUN_FINISHED
