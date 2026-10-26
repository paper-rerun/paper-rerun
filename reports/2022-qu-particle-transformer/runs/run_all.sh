#!/bin/bash
# Full test set: ParT fp32 (main), ParT AMP (variant D9), ParticleNet fp32 (optional). Each step restartable
HERE=/mnt/e/Ciencia/noturno/2022-qu-particle-transformer
PY=$HERE/env/.venv/bin/python
TEST=$HERE/data/JetClass/test_20M
export MPLBACKEND=Agg
cd $HERE/runs
for RUN in "ParT fp32 ParT" "ParT amp ParT" "PN fp32 ParticleNet"
do
	set -- $RUN
	OUT=$HERE/runs/full_$1_$2
	echo "=== $1 $2 start $(date -Is)"
	bash $HERE/runs/predict.sh $1 $2 $OUT $TEST || { echo "predict failed for $1 $2"; continue; }
	if [ ! -f $OUT/score.json ]; then
		$PY -I $HERE/runs/score.py $OUT $3 $OUT/score.json > $OUT/score.log 2>&1
		tail -12 $OUT/score.log
	fi
	echo "=== $1 $2 end $(date -Is)"
done
echo "run_all done"
