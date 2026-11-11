#!/bin/bash
set -euo pipefail
cd /mnt/e/Ciencia/noturno/2025-fallahpour-codontransformer-cego
export OMP_NUM_THREADS=4 MKL_NUM_THREADS=4 MPLBACKEND=Agg
export UV_LINK_MODE=copy HF_HUB_DISABLE_TELEMETRY=1
uv pip install --python ./venv/bin/python "rdata==0.11.2" >/dev/null 2>&1 || true
/usr/bin/time -v nice -n 19 ./venv/bin/python -I scripts/minmax_own.py \
  "data/extracted/Source Data/Fig. 4, Supplementary Fig. 19f-h, 20, 21, 22 and 25.xlsx" \
  data/kodonz results_minmax_own.json
