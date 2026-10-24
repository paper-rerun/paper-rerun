#!/bin/bash
# The MSA-region check on POLG_CXB3N (the one sampled assay whose scores differ from the authors') for the larger sizes
B=/mnt/e/Ciencia/pipeline/2023-notin-proteingym/exec/B2_esm2
"$B/extra_slices.sh" 35M esm2_t12_35M_UR50D POLG_CXB3N_Mattenberger_2021
"$B/extra_slices.sh" 150M esm2_t30_150M_UR50D POLG_CXB3N_Mattenberger_2021
"$B/extra_slices.sh" 650M esm2_t33_650M_UR50D POLG_CXB3N_Mattenberger_2021
