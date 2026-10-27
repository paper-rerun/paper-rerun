#!/bin/bash
# Generate claims.json once and freeze it with its SHA-256 and the time
set -e
export OMP_NUM_THREADS=4 MKL_NUM_THREADS=4 OPENBLAS_NUM_THREADS=4 NUMEXPR_NUM_THREADS=4 MPLBACKEND=Agg
cd /mnt/e/Ciencia/noturno/2022-brout-pantheonplus
if [ -e claims.sha256 ]; then echo "claims.sha256 already exists, not regenerating"; exit 1; fi
nice -n 19 python3 -I gen_claims.py
python3 -I -c "import json;d=json.load(open('claims.json'));print(len(d['claims']),'claims',len(d['definitions']),'definitions')"
HASH=$(sha256sum claims.json | cut -d' ' -f1)
printf '%s  claims.json\nfrozen_utc: %s\n' "$HASH" "$(date -u +%Y-%m-%dT%H:%M:%SZ)" > claims.sha256
cat claims.sha256
