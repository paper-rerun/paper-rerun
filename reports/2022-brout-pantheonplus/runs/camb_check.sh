#!/bin/bash
# CAMB background check for P1 (importance reweighting), then the released-chain likelihood check; one thread each
source /mnt/e/Ciencia/noturno/2022-brout-pantheonplus/env/activate.sh
export OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1
cd runs
nice -n 19 python camb_check.py flcdm_dynesty_s1 > logs/camb_check_flcdm_dynesty_s1.log 2>&1
echo "camb_check exit $?" >> logs/queue_status.txt
nice -n 19 python released_like_check.py > logs/released_like_check.log 2>&1
echo "released_like_check exit $?" >> logs/queue_status.txt
