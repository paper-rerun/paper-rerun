#!/bin/bash
# Smallest GPU example: ESM2 8M, masked-marginals, assay row 17 (B2L11_HUMAN_Dutta_2010_binding-Mcl-1, 198 aa, 170 mutants)
set -eu
W=/mnt/e/Ciencia/pipeline/2023-notin-proteingym
rm -rf "$W/smoke"
time "$W/run_authors_script.sh" 8M 17 "$W/smoke"
source "$W/env/activate.sh"
python -I - "$W/smoke/ESM2/8M/B2L11_HUMAN_Dutta_2010_binding-Mcl-1.csv" <<'PY'
import sys, pandas as pd
from scipy.stats import spearmanr
Scores = pd.read_csv(sys.argv[1])
print(Scores.shape, list(Scores.columns))
print("spearman vs DMS_score:", round(spearmanr(Scores["DMS_score"], Scores["esm2_t6_8M_UR50D"])[0], 4))
PY
