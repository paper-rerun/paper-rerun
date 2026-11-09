#!/usr/bin/env bash
# DESI DR1 BAO + BBN, flat LCDM, with cobaya's Metropolis-Hastings sampler and
# cobaya's own BAO likelihood. This is the authors' pipeline, run as a check on
# our grid: if the MCMC lands where the grid landed, the grid is not the reason
# we sit above the paper's H0.
#
# Four independent chains, four processes, one thread each, so we stay inside
# the 6-thread budget. No MPI here, so each chain gets its own prefix and we
# stitch them into one getdist set afterwards.
set -euo pipefail
ROOT=/mnt/e/Ciencia/noturno/2024-desi-bao-vi
PY="$ROOT/env/venv/bin/python"
cd "$ROOT"
mkdir -p runs/chains runs/logs

export OMP_NUM_THREADS=1
export MPLBACKEND=Agg

for i in 1 2 3 4; do
  sed "s/__SEED__/$((1000 + i))/" runs/scripts/desi_bbn.yaml \
    > "runs/chains/desi_bbn_c${i}.yaml"
  sed -i "s#__PREFIX__#$ROOT/runs/chains/c${i}#" "runs/chains/desi_bbn_c${i}.yaml"
  nice -n 19 "$ROOT/env/venv/bin/cobaya-run" "runs/chains/desi_bbn_c${i}.yaml" \
    > "runs/logs/mcmc_c${i}.log" 2>&1 &
done
wait
echo "all four chains done"

# Stitch into a single getdist set.
cd runs/chains
for i in 1 2 3 4; do
  cp "c${i}.1.txt" "desi_bbn.${i}.txt"
done
cp c1.1.paramnames desi_bbn.paramnames
cp c1.1.ranges desi_bbn.ranges 2>/dev/null || true
wc -l desi_bbn.*.txt
