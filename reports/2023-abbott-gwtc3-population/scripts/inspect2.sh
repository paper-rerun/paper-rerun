#!/bin/bash
set -e
cd /mnt/e/Ciencia/noturno/2023-abbott-gwtc3-population
D=sources/analyses/PowerLawPeak
env/inspect/bin/python -I scripts/inspect_meta.py $D/o1o2o3_mass_c_iid_mag_iid_tilt_powerlaw_redshift_result.json
env/inspect/bin/python -I scripts/inspect_samples_values.py $D/o1o2o3_mass_c_iid_mag_iid_tilt_powerlaw_redshift_samples.hdf5
