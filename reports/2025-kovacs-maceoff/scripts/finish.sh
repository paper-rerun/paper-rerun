#!/bin/bash
# Wait for the large model to finish, then run the comparison and the filter probe.
set -euo pipefail
cd "$(dirname "$0")/.."
until [ -f runs/out/errors_large.csv ] && [ "$(wc -l < runs/out/errors_large.csv)" -ge 50196 ]; do
  sleep 60
done
sleep 30  # let the writer close the file
./env/venv/bin/python -I scripts/compare.py 2>&1 | tee runs/logs/compare.log
./env/venv/bin/python -I scripts/filter_probe.py 2>&1 | tee runs/logs/filter_probe.log
sha256sum -c claims.json.sha256 2>&1 | tee runs/logs/claims_hash_check.log
echo "FINISH_OK"
