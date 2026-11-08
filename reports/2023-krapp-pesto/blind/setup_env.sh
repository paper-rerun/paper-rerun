#!/bin/bash
set -e
export PATH=/root/.local/bin:$PATH
cd /mnt/e/Ciencia/noturno/2023-krapp-pesto-cego
export UV_CACHE_DIR=/mnt/e/Ciencia/noturno/2023-krapp-pesto-cego/.uvcache
uv venv --python 3.11 .venv
. .venv/bin/activate
uv pip install "torch==2.2.2+cpu" --index-url https://download.pytorch.org/whl/cpu
uv pip install numpy==1.26.4 scipy==1.11.4 pandas==2.1.4 scikit-learn==1.3.2 h5py==3.10.0 tqdm gemmi==0.6.5 openpyxl matplotlib
python -c "import torch,numpy,sklearn,gemmi;print(torch.__version__,numpy.__version__,sklearn.__version__,gemmi.__version__)"
