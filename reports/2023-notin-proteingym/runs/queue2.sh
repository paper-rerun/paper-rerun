#!/bin/bash
# ESM-1b with the authors' released setting (confirmed by the probe), then ESM2 650M,
# then the MSA-region diagnostic for 150M/650M, then ESM-1b masked-marginals (paper text, secondary)
W=/mnt/e/Ciencia/meio/2023-notin-proteingym
R=$W/runs/run_model.sh
$R ESM1b esm1b_t33_650M_UR50S.pt ESM1b wt-marginals overlapping
$R ESM2_650M esm2_t33_650M_UR50D.pt ESM2 masked-marginals optimal
export MPLBACKEND=Agg PYTHONUNBUFFERED=1
for M in "esm2_t30_150M_UR50D ESM2_150M" "esm2_t33_650M_UR50D ESM2_650M"; do
	set -- $M
	flock /mnt/e/Ciencia/.gpu.lock $W/env/.venv/bin/python $W/runs/msa_region_hypothesis.py $W/data/weights/$1.pt $2 86 175 130 128 0 >> $W/runs/logs/msa_region_hypothesis.log 2>&1
done
$R ESM1b_masked esm1b_t33_650M_UR50S.pt ESM1b masked-marginals optimal
echo QUEUE2_DONE
