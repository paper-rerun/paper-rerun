#!/bin/bash
source /mnt/e/Ciencia/noturno/2023-abbott-gwtc3-population/env/activate.sh
source /mnt/e/Ciencia/noturno/2023-abbott-gwtc3-population/runs/pp_args.sh
R=/mnt/e/Ciencia/noturno/2023-abbott-gwtc3-population
for f in $R/sources/analyses/PowerLawPeak/o1o2o3_mass_c_iid_mag_iid_tilt_powerlaw_redshift_result.json $R/runs/pp_seed101/result/o1o2o3_mass_c_iid_mag_iid_tilt_powerlaw_redshift_result.json $R/runs/pp_seed202/result/o1o2o3_mass_c_iid_mag_iid_tilt_powerlaw_redshift_result.json; do
  python $R/runs/alt_selection_fix.py $f "${PP_ARGS[@]}" 2>&1 | grep -v "bilby INFO"
done
