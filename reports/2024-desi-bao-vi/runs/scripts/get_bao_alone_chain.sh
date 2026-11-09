#!/usr/bin/env bash
# The authors' own BAO-alone chain, which is the one behind C1 and C2.
set -euo pipefail
B="https://data.desi.lbl.gov/public/dr1/vac/dr1/bao-cosmo-params/v1.0/cobaya/base/desi-bao-all"
D=/mnt/e/Ciencia/noturno/2024-desi-bao-vi/data/official/desi-bao-all
mkdir -p "$D"
cd "$D"
nice -n 19 curl -sS -m 90 "$B/" | grep -oE 'href="[^"]+"' | sed 's/href="//; s/"$//'
for f in chain.input.yaml chain.1.txt chain.2.txt chain.3.txt chain.4.txt; do
  nice -n 19 curl -sSf -m 300 -O "$B/$f" || echo "missing: $f"
done
echo "--- parametrisation ---"
grep -nE "omm|rdh|H0rd|prior|drop|value" chain.input.yaml | head -40
ls -la
