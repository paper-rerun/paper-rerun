#!/bin/bash
W=/mnt/e/Ciencia/noturno/2023-agazie-nanograv15
cd $W/runs
nice -n 19 $W/env/venv/bin/python -I inspect_meta.py $W/sources/repo/tutorials/presampled_cores $W/sources/repo/tutorials/data/optstat_ml_gamma4p33.json
