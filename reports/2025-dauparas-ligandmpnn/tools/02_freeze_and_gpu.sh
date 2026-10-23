#!/bin/bash
# Freeze the environment and prove torch sees the GPU.
set -euo pipefail

UV=$HOME/.local/bin/uv
ROOT=/mnt/e/Ciencia/pipeline/2025-dauparas-ligandmpnn

VIRTUAL_ENV="$ROOT/env" "$UV" pip freeze > "$ROOT/env/requirements.lock.txt"
echo "--- lockfile ---"
wc -l "$ROOT/env/requirements.lock.txt"

echo "--- sources/ ---"
ls -la "$ROOT/sources/"

echo "--- gpu ---"
MPLBACKEND=Agg flock /mnt/e/Ciencia/.gpu.lock "$ROOT/env/bin/python" - <<'PY'
import torch
print("cuda available:", torch.cuda.is_available())
print("device:", torch.cuda.get_device_name(0) if torch.cuda.is_available() else "none")
print("capability:", torch.cuda.get_device_capability(0) if torch.cuda.is_available() else "none")
x = torch.randn(512, 512, device="cuda")
print("matmul ok:", float((x @ x).sum()) == float((x @ x).sum()))
PY
