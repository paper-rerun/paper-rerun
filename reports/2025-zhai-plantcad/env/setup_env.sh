#!/bin/bash
# Build the per-paper venv. Run from WSL.
set -euo pipefail
cd /mnt/e/Ciencia/artigos/2025-zhai-plantcad
export PATH=$HOME/.local/bin:$PATH
uv venv --python 3.11 env/.venv
source env/.venv/bin/activate
uv pip install -r repo/requirements.txt --index-strategy unsafe-best-match
# Prebuilt wheels from the upstream release pages (versions pinned in docs/local-install.md)
uv pip install \
  "https://github.com/state-spaces/mamba/releases/download/v2.2.4/mamba_ssm-2.2.4+cu12torch2.5cxx11abiFALSE-cp311-cp311-linux_x86_64.whl" \
  "https://github.com/Dao-AILab/causal-conv1d/releases/download/v1.5.0.post8/causal_conv1d-1.5.0.post8+cu12torch2.5cxx11abiFALSE-cp311-cp311-linux_x86_64.whl" \
  einops packaging ninja huggingface_hub
uv pip freeze > env/requirements.lock.txt
python -c "import torch, mamba_ssm, causal_conv1d; print(torch.__version__, torch.cuda.is_available(), torch.cuda.get_device_capability())"
