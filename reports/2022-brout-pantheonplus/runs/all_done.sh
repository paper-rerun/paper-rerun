#!/bin/bash
# Exit 0 when every planned fit has its json
cd /mnt/e/Ciencia/noturno/2022-brout-pantheonplus/runs/out 2>/dev/null || cd /e/Ciencia/noturno/2022-brout-pantheonplus/runs/out
for r in flcdm lcdm fwcdm fw0wa4; do for s in 1 2 3; do [ -f ${r}_dynesty_s$s.json ] || exit 1; done; done
for r in fw0wa2_dynesty_s1 sh0esflcdm_dynesty_s1 flcdmmargM_dynesty_s1 flcdm_emcee_s1 lcdm_emcee_s1 fwcdm_emcee_s1 fw0wa4_emcee_s1 fw0wa2_emcee_s1 sh0esflcdm_emcee_s1; do [ -f $r.json ] || exit 1; done
exit 0
