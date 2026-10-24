#!/bin/bash
# D4 probe: score one short (index 1, 852 aa) and one long (index 24, BRCA1 1863 aa) assay with ESM-1b both ways
R=/mnt/e/Ciencia/meio/2023-notin-proteingym/runs/run_model.sh
for I in 1 24; do
	$R probe_ESM1b_wt esm1b_t33_650M_UR50S.pt ESM1b wt-marginals overlapping $I $I
	$R probe_ESM1b_masked esm1b_t33_650M_UR50S.pt ESM1b masked-marginals optimal $I $I
done
echo PROBE_DONE
