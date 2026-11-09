#!/usr/bin/env bash
# The release has two base-LCDM DESI+BBN chains: schoneberg2024-bbn (the one
# that reproduces the published 68.53) and schoneberg2024-bbn-fixed-nnu. Pull
# the second one's input and first chain file to see which omega_b constraint
# IT imposes, so our note to the authors is about the right chain.
set -euo pipefail
B="https://data.desi.lbl.gov/public/dr1/vac/dr1/bao-cosmo-params/v1.0/cobaya/base"
D=/mnt/e/Ciencia/noturno/2024-desi-bao-vi/data/official/sibling-fixed-nnu
mkdir -p "$D"
cd "$D"
for f in chain.input.yaml chain.1.txt chain.2.txt; do
  nice -n 19 curl -sSf -m 300 -O "$B/desi-bao-all_schoneberg2024-bbn-fixed-nnu/$f"
done
echo "--- likelihoods and nnu in the sibling input ---"
grep -nE "schoneberg|nnu|bbn" chain.input.yaml
ls -la
