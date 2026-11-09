#!/bin/bash
# DIAGNOSTIC ONLY, run after our own numbers existed: stats of DESI's published chains
cd /mnt/e/Ciencia/noturno/2024-desi-bao-vi-cego
B=data/desi_chains/cobaya/base
PY="nice -n 19 env/venv/bin/python -I"
head -1 $B/desi-bao-all/chain.1.txt
for d in desi-bao-all_schoneberg2024-bbn desi-bao-all_schoneberg2024-bbn-fixed-nnu; do
  $PY scripts/chain_stats.py $B/$d/chain 0.3 omegam H0 ombh2 rdrag
done
$PY scripts/chain_stats.py $B/desi-bao-all/chain 0.3 omegam omm hrdrag rdh H0rdrag
grep -A8 "^likelihood:" $B/desi-bao-all/chain.updated.yaml
grep -A6 "rdrag\|hrd\|H0:" $B/desi-bao-all/chain.updated.yaml | head -50
