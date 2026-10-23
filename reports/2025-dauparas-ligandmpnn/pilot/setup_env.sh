#!/bin/bash
set -eu
ROOT=/mnt/e/Ciencia/artigos/2025-dauparas-ligandmpnn
UV=/root/.local/bin/uv
cd "$ROOT"
# Venv lives on E: next to the paper, one per paper as the project rules ask
"$UV" venv --python 3.11 .venv
"$UV" pip install --python .venv/bin/python -r repo/requirements.txt
.venv/bin/python - <<'PY'
import torch, prody, numpy
print("torch", torch.__version__, "cuda", torch.cuda.is_available(), torch.version.cuda)
print("prody", prody.__version__, "numpy", numpy.__version__)
if torch.cuda.is_available():
    print("gpu", torch.cuda.get_device_name(0))
PY
"$UV" pip freeze --python .venv/bin/python > env/requirements-lock.txt
echo "lockfile written"
