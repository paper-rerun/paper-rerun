#!/bin/bash
# Final check of the environment stage.
set -euo pipefail

ROOT=/mnt/e/Ciencia/pipeline/2025-dauparas-ligandmpnn

echo "--- repo clean? ---"
git -C "$ROOT/repo" status --porcelain
git -C "$ROOT/repo" log -1 --format="%H %ci"

echo "--- counts ---"
echo "asym:     $(ls "$ROOT/data/structures/asym" | wc -l)"
echo "biounit1: $(ls "$ROOT/data/structures/biounit1" | wc -l)"
echo "weights:  $(ls "$ROOT/data/model_params"/*.pt | wc -l)"

echo "--- tree ---"
ls "$ROOT"
du -sh "$ROOT"/{repo,env,data,logs}
