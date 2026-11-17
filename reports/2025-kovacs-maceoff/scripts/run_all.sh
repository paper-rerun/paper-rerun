#!/bin/bash
# Full run: the three MACE-OFF23 models over the whole released test file,
# one at a time, because there is only one GPU and the user is using the machine.
set -euo pipefail
cd "$(dirname "$0")/.."
for KEY in small medium large; do
  echo "=== $KEY  $(date -u +%FT%TZ)"
  bash scripts/run_model.sh "$KEY" --batch-size 8
done
echo "=== all done $(date -u +%FT%TZ)"
