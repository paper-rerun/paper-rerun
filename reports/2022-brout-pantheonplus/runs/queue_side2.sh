#!/bin/bash
# Second side queue, 1 slot: the main list from the end (locks keep the two queues apart)
NPAR=1 bash /mnt/e/Ciencia/noturno/2022-brout-pantheonplus/runs/run_queue.sh \
  fw0wa2_dynesty_s1 fw0wa4_dynesty_s3 fw0wa4_dynesty_s2 fwcdm_dynesty_s3 fwcdm_dynesty_s2 lcdm_dynesty_s3 lcdm_dynesty_s2
