#!/bin/bash
# Side queue, 1 slot: emcee variants from the end of the main list, then the CAMB check
cd /mnt/e/Ciencia/noturno/2022-brout-pantheonplus/runs
NPAR=1 bash run_queue.sh sh0esflcdm_emcee_s1 fw0wa2_emcee_s1 fw0wa4_emcee_s1 fwcdm_emcee_s1 lcdm_emcee_s1
until [ -f out/flcdm_dynesty_s1.json ]; do sleep 30; done
source /mnt/e/Ciencia/noturno/2022-brout-pantheonplus/env/activate.sh
export OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1
nice -n 19 python camb_check.py flcdm_dynesty_s1 > logs/camb_check_flcdm_dynesty_s1.log 2>&1
echo "camb_check exit $?" >> logs/queue_status.txt
