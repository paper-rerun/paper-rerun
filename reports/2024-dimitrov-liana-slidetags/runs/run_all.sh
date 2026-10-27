#!/bin/bash
# Full pipeline, restartable (every step skips finished outputs). Light mode: nice 19, 4 threads, one process at a time
# (layer B uses joblib n_jobs=4 = at most 4 worker processes).
set -e
source /mnt/e/Ciencia/noturno/2024-dimitrov-liana-slidetags/runs/env.sh
cd $R/runs
echo "start $(date -Is)"
for k in SCP2167 SCP2169 SCP2170 SCP2171 SCP2176; do
  /usr/bin/time -v $PY truth.py $k > logs/truth_$k.log 2>&1
  grep -E "seconds|skip|Maximum resident|Elapsed" logs/truth_$k.log
done
echo "truth done $(date -Is)"
for r in R0 V1; do
  /usr/bin/time -v $PY evaluate.py --reading $r > logs/eval_${r}_figshare.log 2>&1
  tail -1 logs/eval_${r}_figshare.log; grep -E "Elapsed|Maximum resident" logs/eval_${r}_figshare.log
done
$PY evaluate.py --reading V2 --methods Rank_Aggregate > logs/eval_V2_figshare.log 2>&1
$PY evaluate.py --reading V3 --methods scSeqComm > logs/eval_V3_figshare.log 2>&1
/usr/bin/time -v $PY evaluate.py --reading V4 > logs/eval_V4_figshare.log 2>&1
echo "layer A + variants done $(date -Is)"
/usr/bin/time -v $PY layerB.py > logs/layerB.log 2>&1
grep -E "Elapsed|Maximum resident|done" logs/layerB.log
/usr/bin/time -v $PY evaluate.py --reading R0 --uns layerB > logs/eval_R0_layerB.log 2>&1
echo "all done $(date -Is)"
