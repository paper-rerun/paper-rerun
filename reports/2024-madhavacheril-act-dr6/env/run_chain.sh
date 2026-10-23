#!/usr/bin/env bash
# Run one Cobaya MCMC with MPI chains
# usage: run_chain.sh <yaml> <n_chains> <threads_per_chain> <log>
D=/mnt/e/Ciencia/artigos/2024-madhavacheril-act-dr6
cd $D
source ${VENV:-.venv-pinned}/bin/activate
export OMP_NUM_THREADS=$3
export MPLBACKEND=Agg
export COBAYA_PACKAGES_PATH=$D/packages
mpirun --allow-run-as-root --bind-to none -n $2 -x OMP_NUM_THREADS -x COBAYA_PACKAGES_PATH cobaya-run --resume $1 > $4 2>&1
echo "exit=$?" >> $4
