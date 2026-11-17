#!/bin/bash
# Build the frozen environment for the MACE-OFF23 reproduction.
# Versions are pinned to the era of the pinned repo commit (2025-01-29), the
# commit that carries the MACE-OFF23 weights we evaluate.
set -euo pipefail
cd "$(dirname "$0")/.."
ROOT="$PWD"

uv venv --python 3.10 "$ROOT/env/venv"
export VIRTUAL_ENV="$ROOT/env/venv"

# torch first, from the PyTorch CUDA index. That index publishes no upload
# dates, so the --exclude-newer filter cannot be used on it.
uv pip install --python "$ROOT/env/venv/bin/python" \
  --index-url https://download.pytorch.org/whl/cu121 \
  torch==2.5.1+cu121

# Everything else from PyPI, frozen to 2025-01-29.
uv pip install --python "$ROOT/env/venv/bin/python" \
  --exclude-newer 2025-01-29 \
  -r "$ROOT/env/requirements.in"

"$ROOT/env/venv/bin/python" -c "import torch, mace, ase, numpy; print('torch', torch.__version__, 'cuda', torch.version.cuda, torch.cuda.is_available()); print('mace', mace.__version__); print('ase', ase.__version__); print('numpy', numpy.__version__)"
uv pip freeze --python "$ROOT/env/venv/bin/python" > "$ROOT/env/requirements.freeze.txt"
