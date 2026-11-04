#!/bin/bash
source /mnt/e/Ciencia/noturno/2023-abbott-gwtc3-population/env/activate.sh
R=/mnt/e/Ciencia/noturno/2023-abbott-gwtc3-population/runs
python $R/evaluate.py $R/pp_seed101/result/o1o2o3_mass_c_iid_mag_iid_tilt_powerlaw_redshift_result.json $R/pp_seed202/result/o1o2o3_mass_c_iid_mag_iid_tilt_powerlaw_redshift_result.json > $R/evaluation.log 2>&1
