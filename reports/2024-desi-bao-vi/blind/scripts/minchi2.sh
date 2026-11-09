#!/bin/bash
cd /mnt/e/Ciencia/noturno/2024-desi-bao-vi-cego
B=data/desi_chains/cobaya/base/desi-bao-all
for f in $B/chain.[1-4].txt; do awk 'NR>1 && (m=="" || $20<m){m=$20} END{print FILENAME, "min chi2__BAO", m}' $f; done
