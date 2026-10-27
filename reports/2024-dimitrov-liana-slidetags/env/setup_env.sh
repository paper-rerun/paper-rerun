#!/bin/bash
# Build the frozen env: Python 3.10.13 + authors' pins. Unpinned deps resolved as of 2024-05-15 (env.yml freeze date range)
set -e
export PATH=$HOME/.local/bin:$PATH
cd /mnt/e/Ciencia/noturno/2024-dimitrov-liana-slidetags/env
echo "933caee33e70e4760d07ee722b5e5679  wheels/liana-1.0.5-py3-none-any.whl" | md5sum -c
uv python install 3.10.13
if [ ! -f requirements.lock ]; then
  uv pip compile requirements.in --python-version 3.10 --exclude-newer 2024-05-15 --generate-hashes -o requirements.lock
fi
# venv lives on the Linux fs (numba cache and speed); recreated from the lock
VENV=$HOME/venvs/liana-slidetags
uv venv --python 3.10.13 --clear $VENV
VIRTUAL_ENV=$VENV uv pip sync --python $VENV/bin/python requirements.lock
$VENV/bin/python -c "import sys, liana, numpy, pandas, scanpy, anndata, decoupler, sklearn, numba, scipy; print(sys.version); print('liana', liana.__version__, 'numpy', numpy.__version__, 'pandas', pandas.__version__, 'scanpy', scanpy.__version__, 'anndata', anndata.__version__, 'decoupler', decoupler.__version__, 'sklearn', sklearn.__version__, 'numba', numba.__version__, 'scipy', scipy.__version__)"
VIRTUAL_ENV=$VENV uv pip freeze --python $VENV/bin/python > pip_freeze.txt
