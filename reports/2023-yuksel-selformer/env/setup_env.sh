#!/bin/bash
# Build the env once and freeze it. Versions come from the repo's data/requirements.yml
set -e
cd /mnt/e/Ciencia/noturno/2023-yuksel-selformer/env
export UV_LINK_MODE=copy
UV=~/.local/bin/uv
if [ ! -f requirements.lock ]; then
	$UV pip compile requirements.in --python-version 3.10 --exclude-newer 2023-06-29 -o requirements.lock
fi
[ -d .venv ] || $UV venv --python 3.10 .venv
# torch 1.13.1 CPU build first, so nothing else drags in a CUDA wheel
$UV pip install --python .venv/bin/python --index-url https://download.pytorch.org/whl/cpu torch==1.13.1+cpu
$UV pip install --python .venv/bin/python -r requirements.lock
.venv/bin/python -c "import torch, transformers, chemprop, selfies, sklearn, pandas, numpy, rdkit; print('ok', torch.__version__, transformers.__version__, chemprop.__version__, selfies.__version__, sklearn.__version__, numpy.__version__)"
.venv/bin/python -c "from importlib.metadata import version; print('simpletransformers', version('simpletransformers'))"
.venv/bin/python --version
$UV pip freeze --python .venv/bin/python > requirements.freeze.txt
