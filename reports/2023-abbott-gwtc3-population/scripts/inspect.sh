#!/bin/bash
set -e
export MPLBACKEND=Agg
cd /mnt/e/Ciencia/noturno/2023-abbott-gwtc3-population
export PATH=$HOME/.local/bin:$PATH
[ -d env/inspect ] || uv venv -q -p 3.11 env/inspect
uv pip install -q -p env/inspect/bin/python numpy h5py
D=sources/analyses/PowerLawPeak
env/inspect/bin/python -I scripts/inspect_result.py $D/o1o2o3_mass_c_iid_mag_iid_tilt_powerlaw_redshift_result.json
env/inspect/bin/python -I scripts/inspect_samples.py $D/o1o2o3_mass_c_iid_mag_iid_tilt_powerlaw_redshift_samples.hdf5
