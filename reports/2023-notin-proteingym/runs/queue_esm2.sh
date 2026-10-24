#!/bin/bash
R=/mnt/e/Ciencia/meio/2023-notin-proteingym/runs/run_model.sh
$R ESM2_8M esm2_t6_8M_UR50D.pt ESM2 masked-marginals optimal
$R ESM2_35M esm2_t12_35M_UR50D.pt ESM2 masked-marginals optimal
$R ESM2_150M esm2_t30_150M_UR50D.pt ESM2 masked-marginals optimal
echo QUEUE_DONE
