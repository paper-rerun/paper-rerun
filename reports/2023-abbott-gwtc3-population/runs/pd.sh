#!/bin/bash
source /mnt/e/Ciencia/noturno/2023-abbott-gwtc3-population/env/activate.sh
cd /mnt/e/Ciencia/noturno/2023-abbott-gwtc3-population
python - <<'PY'
import json
pub = json.load(open("sources/analyses/PowerLawPeak/o1o2o3_mass_c_iid_mag_iid_tilt_powerlaw_redshift_result.json"))["priors"]
ours = json.load(open("runs/pp_seed101/result/o1o2o3_mass_c_iid_mag_iid_tilt_powerlaw_redshift_result.json"))["priors"]
for k in sorted(set(pub) | set(ours)):
    if pub.get(k) != ours.get(k): print(k, "\n  pub ", pub.get(k), "\n  ours", ours.get(k))
PY
