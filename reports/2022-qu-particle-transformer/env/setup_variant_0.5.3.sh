#!/bin/bash
# Variant env (D10): weaver-core 0.5.3, deps resolved as of 2026-06-24, 2 days after the v0.5.3 tag (2026-06-22), same torch 2.4.1+cu121
# If requirements-0.5.3.lock exists, rebuild exactly from it
set -eu
HERE=/mnt/e/Ciencia/noturno/2022-qu-particle-transformer
UV=$HOME/.local/bin/uv
PY=$HERE/env/.venv-0.5.3/bin/python
CUTOFF=2026-06-24
export UV_LINK_MODE=copy
cd $HERE/env
[ -d .venv-0.5.3 ] || $UV venv --python 3.10 .venv-0.5.3
if [ -f requirements-0.5.3.lock ]; then
	$UV pip sync --python $PY requirements-0.5.3.lock --index-strategy unsafe-best-match \
		--extra-index-url https://download.pytorch.org/whl/cu121
else
	$UV pip compile --python-version 3.10 --exclude-newer $CUTOFF weaver-core-0.5.3-src/requirements.txt -o weaver-0.5.3-deps.lock
	$UV pip sync --python $PY weaver-0.5.3-deps.lock
	$UV pip install --python $PY torch==2.4.1 --index-url https://download.pytorch.org/whl/cu121
	$UV pip freeze --python $PY > requirements-0.5.3.lock
fi
$UV pip install --python $PY --no-deps $HERE/env/weaver-core-0.5.3-src
$PY -c "import torch,numpy,uproot,awkward,sklearn,weaver;print('torch',torch.__version__,'cuda',torch.cuda.is_available(),'numpy',numpy.__version__,'uproot',uproot.__version__,'awkward',awkward.__version__,'sklearn',sklearn.__version__)"
