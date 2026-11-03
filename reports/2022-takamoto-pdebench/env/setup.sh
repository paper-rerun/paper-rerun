#!/bin/bash
# Rebuild the environment from the lockfile. Run in WSL Ubuntu.
set -e
E=/mnt/e/Ciencia/noturno/2022-takamoto-pdebench/env
UV=~/.local/bin/uv
export UV_PYTHON_INSTALL_DIR=$E/python UV_CACHE_DIR=$E/.uvcache UV_LINK_MODE=copy
# venv and interpreter inside env/ (stay in the working folder); lockfile lives in env/
V=$E/.venv
$UV python install 3.9.25
[ -d $V ] || $UV venv -p $E/python/cpython-3.9.25-linux-x86_64-gnu/bin/python3.9 $V
if [ ! -f $E/requirements.lock ]; then
  $UV pip compile $E/requirements.in -p 3.9 --extra-index-url https://download.pytorch.org/whl/cpu --index-strategy unsafe-best-match -o $E/requirements.lock
fi
VIRTUAL_ENV=$V $UV pip sync $E/requirements.lock --extra-index-url https://download.pytorch.org/whl/cpu --index-strategy unsafe-best-match
# pdebench itself from the pinned clone, without deps (deps are in the lock)
VIRTUAL_ENV=$V $UV pip install --no-deps -e /mnt/e/Ciencia/noturno/2022-takamoto-pdebench/repo
$V/bin/python -c "import torch,numpy,h5py,hydra;print(torch.__version__,numpy.__version__,h5py.__version__,hydra.__version__)"
