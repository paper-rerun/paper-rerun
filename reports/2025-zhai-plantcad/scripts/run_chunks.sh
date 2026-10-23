#!/bin/bash
# Round-robin over tasks, one chunk per GPU-lock hold, so other agents get the GPU between chunks.
# Authors' predict_XGBoost.py and released l32 classifiers, unchanged; batch 8 is the most that fits 8 GB.
source /mnt/e/Ciencia/artigos/2025-zhai-plantcad/env/activate.sh
export HF_HUB_OFFLINE=1
Tasks="TIS_valid Donor_valid TIS_sorghum TIS_maize Donor_sorghum Donor_maize"
for Index in $(seq -f "%03g" 0 10); do
	for Task in $Tasks; do
		Chunk=chunks/$Task/chunk_$Index.tsv
		Output=runs/$Task
		[ -f "$Chunk" ] || continue
		[ -f "$Output/chunk_${Index}_predictions.tsv" ] && continue
		Classifier=repo/classifiers/PlantCaduceus_l32/${Task%%_*}_XGBoost.json
		echo "$(date '+%F %T') start $Task $Index"
		flock /mnt/e/Ciencia/.gpu.lock python repo/src/predict_XGBoost.py -test $Chunk -model kuleshov-group/PlantCaduceus_l32 \
			-classifier $Classifier -device cuda:0 -batchSize 8 -output $Output > logs/run_${Task}_${Index}.log 2>&1 \
			&& echo "$(date '+%F %T') done $Task $Index" || echo "$(date '+%F %T') FAILED $Task $Index"
	done
done
echo "$(date '+%F %T') all chunks finished"
