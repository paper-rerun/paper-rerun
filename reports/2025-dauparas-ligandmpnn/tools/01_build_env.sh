#!/bin/bash
# Build the LigandMPNN environment from the authors' own pins.
set -euo pipefail

UV=$HOME/.local/bin/uv
ROOT=/mnt/e/Ciencia/pipeline/2025-dauparas-ligandmpnn

cd "$ROOT"

# Authors' README says python=3.11, so start there
"$UV" venv --clear --python 3.11 "$ROOT/env"

# requirements.txt carries the exact pins they shipped, cu121 nvidia wheels included
VIRTUAL_ENV="$ROOT/env" "$UV" pip install -r "$ROOT/repo/requirements.txt"

# ProDy 2.4.1 imports pkg_resources, dropped in setuptools 81, so hold setuptools back
VIRTUAL_ENV="$ROOT/env" "$UV" pip install "setuptools<81"

"$ROOT/env/bin/python" -c "import torch, numpy, prody, Bio; print('torch', torch.__version__, 'numpy', numpy.__version__, 'prody', prody.__version__)"
