#!/bin/bash
cd /mnt/e/Ciencia/noturno/2024-dimitrov-liana-slidetags
OMP_NUM_THREADS=4 nice -n 19 python3 -I scripts/paper_values.py sources/MOESM7_ESM.xlsx sources/fig4_source_data.tsv sources/fig4_source_medians.json
