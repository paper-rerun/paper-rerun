#!/bin/bash
# Full-sequence and MSA-region scores for the other 4 region-scored assays at the larger sizes (not in the 30-assay sample),
# used only for the projected full-217 value in extra_projection.py
B=/mnt/e/Ciencia/pipeline/2023-notin-proteingym/exec/B2_esm2
Assays="A0A140D2T1_ZIKV_Sourisseau_2019 KCNH2_HUMAN_Kozek_2020 POLG_HCVJF_Qi_2014 SCN5A_HUMAN_Glazer_2019"
"$B/extra_slices.sh" 35M esm2_t12_35M_UR50D $Assays
"$B/extra_slices.sh" 150M esm2_t30_150M_UR50D $Assays
"$B/extra_slices.sh" 650M esm2_t33_650M_UR50D $Assays
