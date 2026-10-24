#!/bin/bash
set -e
D=/mnt/e/Ciencia/meio/2023-notin-proteingym/data/weights
mkdir -p $D; cd $D
for m in esm2_t6_8M_UR50D esm2_t12_35M_UR50D esm2_t30_150M_UR50D esm1b_t33_650M_UR50S esm2_t33_650M_UR50D; do
  wget -q -c https://dl.fbaipublicfiles.com/fair-esm/models/$m.pt
done
ls -la; sha256sum *.pt > SHA256SUMS; cat SHA256SUMS
