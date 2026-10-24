#!/bin/bash
set -eu
W=/mnt/e/Ciencia/pipeline/2023-notin-proteingym
cd "$W/data"
[ -d DMS_ProteinGym_substitutions ] || unzip -q DMS_ProteinGym_substitutions.zip
ls DMS_ProteinGym_substitutions | wc -l
source "$W/env/activate.sh"
python -I - "$W/repo/reference_files/DMS_substitutions.csv" <<'PY'
import sys, pandas as pd
Ref = pd.read_csv(sys.argv[1])
print(len(Ref), Ref["DMS_total_number_mutants"].sum(), Ref["UniProt_ID"].nunique(), (Ref["seq_len"] > 1022).sum())
Ref["row_index"] = range(len(Ref))
print(Ref.sort_values(["DMS_total_number_mutants", "seq_len"])[["row_index", "DMS_id", "seq_len", "DMS_total_number_mutants"]].head(5).to_string())
PY
