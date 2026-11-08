#!/bin/bash
# Rebuild the env from the frozen lockfile
set -e
cd /mnt/e/Ciencia/noturno/2023-krapp-pesto/env
export UV_LINK_MODE=copy
UV=~/.local/bin/uv
if [ ! -f requirements.lock ]; then
	$UV pip compile requirements.in --python-version 3.9 --exclude-newer 2022-07-12 -o requirements.lock
fi
[ -d .venv ] || $UV venv --python 3.9 .venv
$UV pip install --python .venv/bin/python -r requirements.lock
# torch 1.11.0 (Mar 2022), CPU build, from the official PyTorch index
$UV pip install --python .venv/bin/python --no-deps --index-url https://download.pytorch.org/whl/cpu torch==1.11.0+cpu typing-extensions==4.3.0
.venv/bin/python -c "import torch, gemmi, h5py, numpy, pandas, sklearn, scipy; print('ok', torch.__version__, numpy.__version__, pandas.__version__, sklearn.__version__, gemmi.__version__, h5py.__version__)"
.venv/bin/python --version
$UV pip freeze --python .venv/bin/python > requirements.freeze.txt
