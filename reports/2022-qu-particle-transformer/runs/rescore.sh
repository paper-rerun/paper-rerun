#!/bin/bash
# Re-score all full runs with the fixed score.py (same predictions)
H=/mnt/e/Ciencia/noturno/2022-qu-particle-transformer
cd $H/runs
for RUN in "ParT_fp32 ParT" "ParT_amp ParT" "PN_fp32 ParticleNet"
do
	set -- $RUN
	$H/env/.venv/bin/python -I $H/runs/score.py $H/runs/full_$1 $2 $H/runs/full_$1/score.json > $H/runs/full_$1/score.log 2>&1
	echo "== $1"; grep -vi warn $H/runs/full_$1/score.log | grep -E "^accuracy|status|Error"
done
$H/env/.venv/bin/python test_score.py
