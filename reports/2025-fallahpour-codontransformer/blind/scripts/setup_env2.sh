#!/bin/bash
set -euo pipefail
cd /mnt/e/Ciencia/noturno/2025-fallahpour-codontransformer-cego
export UV_LINK_MODE=copy
VP=./venv/bin/python
uv pip install --python "$VP" --index-strategy unsafe-best-match \
  --extra-index-url https://download.pytorch.org/whl/cpu \
  "torch==2.5.1+cpu" "transformers==4.46.3" "CodonTransformer==1.6.7"
uv pip freeze --python "$VP" > env-freeze-stage2.txt
$VP -I -c "import torch,transformers;print(torch.__version__,transformers.__version__)"
