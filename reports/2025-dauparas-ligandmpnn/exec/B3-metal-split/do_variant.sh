#!/usr/bin/env bash
set -euo pipefail
ROOT=/mnt/e/Ciencia/pipeline/2025-dauparas-ligandmpnn
source "$ROOT/env/activate.sh"
python "$ROOT/exec/B3-metal-split/variants.py" "$@"
