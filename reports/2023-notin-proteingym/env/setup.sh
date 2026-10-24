#!/bin/bash
# Rebuilds the venv from the lockfile. Python 3.10 because torch 1.13.1 has no wheels past 3.10
set -e
W=/mnt/e/Ciencia/meio/2023-notin-proteingym
UV=~/.local/bin/uv
# everything (venv, python, uv cache) stays inside the working folder
V=$W/env/.venv
export UV_PYTHON_INSTALL_DIR=$W/env/.uv-python UV_CACHE_DIR=$W/env/.uv-cache UV_LINK_MODE=copy
$UV python install 3.10
[ -d $V ] || $UV venv -p 3.10 $V
if [ ! -f $W/env/requirements.lock ]; then
  $UV pip compile $W/env/requirements.in -p 3.10 --extra-index-url https://download.pytorch.org/whl/cu117 --index-strategy unsafe-best-match -o $W/env/requirements.lock
fi
VIRTUAL_ENV=$V $UV pip sync $W/env/requirements.lock --extra-index-url https://download.pytorch.org/whl/cu117 --index-strategy unsafe-best-match
$V/bin/python -c "import torch,numpy,pandas,scipy,sklearn;print(torch.__version__,torch.cuda.is_available(),torch.cuda.get_device_name(0),numpy.__version__,pandas.__version__,scipy.__version__,sklearn.__version__)"
