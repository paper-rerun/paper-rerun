#!/bin/bash
# Score whatever stats exist. Args are passed through to score_recovery.py.
R=/mnt/e/Ciencia/artigos/2025-dauparas-ligandmpnn
cd "$R"
export OMP_NUM_THREADS=4 MKL_NUM_THREADS=4 MPLBACKEND=Agg
.venv/bin/python score_recovery.py "$@" 2>&1 | grep -vE 'pkg_resources|ProDy|UserWarning|^  import'
