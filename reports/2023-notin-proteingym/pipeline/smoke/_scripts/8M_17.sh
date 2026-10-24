#!/bin/bash 

source /mnt/e/Ciencia/pipeline/2023-notin-proteingym/runs_tmp.vE5KBJ/zero_shot_config.sh
source /mnt/e/Ciencia/pipeline/2023-notin-proteingym/env/activate.sh

# Run whichever size of ESM2 by uncommenting the appropriate pair of lines below

export model_checkpoint="/mnt/e/Ciencia/pipeline/2023-notin-proteingym/data/weights/esm2_t6_8M_UR50D.pt"
export dms_output_folder=${DMS_output_score_folder_subs}/ESM2/8M

# export model_checkpoint="path to 35M ESM2 checkpoint"
# export dms_output_folder=${DMS_output_score_folder_subs}/ESM2/35M

# export model_checkpoint="path to 150M ESM2 checkpoint"
# export dms_output_folder=${DMS_output_score_folder_subs}/ESM2/150M

# export model_checkpoint="path to 650M ESM2 checkpoint"
# export dms_output_folder=${DMS_output_score_folder_subs}/ESM2/650M

# export model_checkpoint="path to 3B ESM2 checkpoint"
# export dms_output_folder=${DMS_output_score_folder_subs}/ESM2/3B

# export model_checkpoint="path to 15B ESM2 checkpoint"
# export dms_output_folder=${DMS_output_score_folder_subs}/ESM2/15B

## Regression weights are at: https://dl.fbaipublicfiles.com/fair-esm/regression/esm2_t33_650M_UR50S-contact-regression.pt
#https://dl.fbaipublicfiles.com/fair-esm/regression/esm2_t33_650M_UR50S-contact-regression.pt

export model_type="ESM2"
export scoring_strategy="masked-marginals"
export DMS_index=17

python ../../proteingym/baselines/esm/compute_fitness.py \
    --model-location ${model_checkpoint} \
    --dms_index $DMS_index \
    --dms_mapping ${DMS_reference_file_path_subs} \
    --dms-input ${DMS_data_folder_subs} \
    --dms-output ${dms_output_folder} \
    --scoring-strategy ${scoring_strategy} \
    --model_type ${model_type} 