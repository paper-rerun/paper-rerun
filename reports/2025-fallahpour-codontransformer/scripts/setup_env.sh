#!/bin/bash
# Build the analysis venv. Light mode: CPU-only torch, 4 threads.
# Versions resolved as of the pinned repo commit date (2025-07-27) with --exclude-newer.
export PATH="$HOME/.local/bin:$PATH"
set -euo pipefail
ROOT=/mnt/e/Ciencia/noturno/2025-fallahpour-codontransformer
cd "$ROOT/env"
uv venv --clear --python 3.11 .venv
# shellcheck disable=SC1091
source .venv/bin/activate
uv pip install --exclude-newer 2025-07-28 \
  openpyxl pandas numpy dtw-python CAI-PyPI biopython
# The PyTorch CPU index carries no upload dates, so --exclude-newer refuses everything there.
# Pin the version by hand instead: 2.7.1 is the newest release before the pinned commit (2025-07-27).
uv pip install --index-url https://download.pytorch.org/whl/cpu "torch==2.7.1+cpu"
uv pip install --exclude-newer 2025-07-28 transformers
uv pip freeze > requirements.freeze.txt
python -c "import torch, transformers, numpy, pandas; print(torch.__version__, transformers.__version__, numpy.__version__, pandas.__version__)"

# Extra dependencies of the authors' inference path (CodonPrediction -> CodonData -> CodonUtils).
# numpy is pinned below 2 because requirements.txt asks for numpy>=1.26.4,<2.0.
uv pip install --exclude-newer 2025-07-28 "numpy<2" onnxruntime python_codon_tables scikit-learn tqdm requests
uv pip freeze > requirements.freeze.txt
