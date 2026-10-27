#!/bin/bash
export OMP_NUM_THREADS=4 MKL_NUM_THREADS=4 OPENBLAS_NUM_THREADS=4 NUMEXPR_NUM_THREADS=4 MPLBACKEND=Agg
W=/mnt/e/Ciencia/noturno/2026-gilchrist-foldmason
nice -n 19 python3 -I "$W/scripts/summarise_author_scores.py" "$W/sources/analysis" > "$W/sources/author_scores_summary.txt"
