#!/bin/bash
# Cropped-sequence alternative for the 5 assays whose MSA covers only part of target_seq, 35M/150M/650M
W=/mnt/e/Ciencia/pipeline/2023-notin-proteingym
Ids="KCNH2_HUMAN_Kozek_2020 SCN5A_HUMAN_Glazer_2019 POLG_CXB3N_Mattenberger_2021 POLG_HCVJF_Qi_2014 A0A140D2T1_ZIKV_Sourisseau_2019"
for Pair in "esm2_t12_35M_UR50D crop_35M" "esm2_t30_150M_UR50D crop_150M" "esm2_t33_650M_UR50D crop_650M"; do
	set -- $Pair
	bash "$W/verify/scripts/crop_test.sh" "$1" ESM2 "$2" $Ids > "$W/verify/logs/crop_test_$2.log" 2>&1 || echo "FAILED $2"
	echo "=== crop $2 $(grep -c '^DONE' "$W/verify/logs/crop_test_$2.log")"
done
