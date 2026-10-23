#!/bin/bash
# Score every task on the chunks finished so far
source /mnt/e/Ciencia/artigos/2025-zhai-plantcad/env/activate.sh
python scripts/score_sample.py chunks/TIS_valid runs/TIS_valid 1.0 --uniform
python scripts/score_sample.py chunks/Donor_valid runs/Donor_valid 1.0 --uniform
python scripts/score_sample.py chunks/TIS_sorghum runs/TIS_sorghum 1.0
python scripts/score_sample.py chunks/TIS_maize runs/TIS_maize 1.0
python scripts/score_sample.py chunks/Donor_sorghum runs/Donor_sorghum 0.25
python scripts/score_sample.py chunks/Donor_maize runs/Donor_maize 0.25
