#!/bin/bash
# Build the pinned Linux environment inside the project folder (never in the WSL root).
# The uv cache has to live on the WSL ext4 side: renames fail on the /mnt/e drvfs mount.
# /tmp/selformer-uvcache is removed again by scripts/cleanup_wsl.sh.
set -e
export PATH="/root/.local/bin:$PATH"
BASE=/mnt/e/Ciencia/noturno/2023-yuksel-selformer-cego
export UV_CACHE_DIR=/tmp/selformer-uvcache
export UV_LINK_MODE=copy
mkdir -p "$UV_CACHE_DIR"
cd "$BASE/env"
rm -rf venv-linux
uv venv --python 3.10 venv-linux
uv pip install --python venv-linux/bin/python \
  --index-strategy unsafe-best-match \
  --index-url https://pypi.org/simple \
  --extra-index-url https://download.pytorch.org/whl/cu117 \
  "torch==1.13.1+cu117"
uv pip install --python venv-linux/bin/python \
  "transformers==4.26.1" "tokenizers==0.13.2" "datasets==2.9.0" \
  "scikit-learn==1.2.1" "selfies==2.1.1" "pandarallel==1.6.4" \
  "numpy==1.23.5" "pandas==1.5.3" "pyarrow==14.0.2" \
  "chemprop==1.5.2" "rdkit-pypi==2022.9.5" \
  "simpletransformers==0.63.9" "wandb==0.13.10"
uv pip install --python venv-linux/bin/python \
  "transformers==4.26.1" "tokenizers==0.13.2" "datasets==2.9.0" \
  "numpy==1.23.5" "pandas==1.5.3"
uv pip freeze --python venv-linux/bin/python > "$BASE/lockfile-requirements-linux.txt"
"$BASE/env/venv-linux/bin/python" -c "import torch;print('cuda',torch.cuda.is_available(),torch.__version__)"
echo DONE
