#!/bin/bash
# Main queue, 3 slots while the margM smoke test still runs in the 4th
NPAR=3 bash /mnt/e/Ciencia/noturno/2022-brout-pantheonplus/runs/run_queue.sh \
  flcdm_dynesty_s1 lcdm_dynesty_s1 fwcdm_dynesty_s1 fw0wa4_dynesty_s1 flcdm_emcee_s1 sh0esflcdm_dynesty_s1 \
  flcdm_dynesty_s2 flcdm_dynesty_s3 lcdm_dynesty_s2 lcdm_dynesty_s3 fwcdm_dynesty_s2 fwcdm_dynesty_s3 \
  fw0wa4_dynesty_s2 fw0wa4_dynesty_s3 fw0wa2_dynesty_s1 \
  lcdm_emcee_s1 fwcdm_emcee_s1 fw0wa4_emcee_s1 fw0wa2_emcee_s1 sh0esflcdm_emcee_s1
