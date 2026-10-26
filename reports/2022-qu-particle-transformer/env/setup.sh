#!/bin/bash
# Build the Python env for the ParT reproduction (WSL2 Ubuntu 24.04, CUDA GPU)
# Python 3.10 as in the weaver-core README; weaver-core 0.4.17 from the local git checkout (tag v0.4.17)
# weaver-core deps resolved as they were on 2024-08-07 (uv --exclude-newer), the day after 0.4.17 was tagged
# torch 2.4.1+cu121: weaver-core pins no torch; 2.4 was current in Aug 2024
# If requirements.lock exists, rebuild exactly from it
set -eu
HERE=/mnt/e/Ciencia/noturno/2022-qu-particle-transformer
UV=$HOME/.local/bin/uv
PY=$HERE/env/.venv/bin/python
export UV_LINK_MODE=copy
cd $HERE/env
[ -d .venv ] || $UV venv --python 3.10 .venv
if [ -f requirements.lock ]; then
	$UV pip sync --python $PY requirements.lock --index-strategy unsafe-best-match \
		--extra-index-url https://download.pytorch.org/whl/cu121
else
	$UV pip compile --python-version 3.10 --exclude-newer 2024-08-07 $HERE/weaver-core-src/requirements.txt -o weaver-deps.lock
	$UV pip sync --python $PY weaver-deps.lock
	$UV pip install --python $PY torch==2.4.1 --index-url https://download.pytorch.org/whl/cu121
	$UV pip freeze --python $PY > requirements.lock
fi
# weaver itself, no deps, from the tagged checkout
$UV pip install --python $PY --no-deps $HERE/weaver-core-src
$PY -c "import torch,numpy,uproot,awkward,sklearn,weaver;print('torch',torch.__version__,'cuda',torch.cuda.is_available(),'numpy',numpy.__version__,'uproot',uproot.__version__,'awkward',awkward.__version__,'sklearn',sklearn.__version__)"
