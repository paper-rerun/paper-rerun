#!/bin/bash
# Build the venv for matgl 1.3.0 (DGL backend). Run from WSL.
# REBUILD_FROM_LOCK=1 reinstalls exactly env/requirements.lock.txt instead of resolving again
set -euo pipefail
cd /mnt/e/Ciencia/noturno/2025-ko-matgl
export PATH=$HOME/.local/bin:$PATH
export UV_LINK_MODE=copy
uv venv --clear --python 3.11 env/.venv
source env/.venv/bin/activate
INDEXES="--extra-index-url https://download.pytorch.org/whl/cu121 --find-links https://data.dgl.ai/wheels/torch-2.4/cu121/repo.html --index-strategy unsafe-best-match"
if [ "${REBUILD_FROM_LOCK:-0}" = 1 ]; then
  uv pip install -r env/requirements.lock.txt $INDEXES
else
  # Upper bounds from matgl v1.3.0 pyproject (linux): torch<=2.4.0, dgl<=2.4.0, torchdata<=0.8.0, numpy<2
  # ase and pymatgen pinned to releases before the v1.3.0 tag (2025-08-12): ase 3.29 removed ExpCellFilter, which matgl.ext.ase imports
  uv pip install "torch==2.4.0" "dgl==2.4.0+cu121" "torchdata==0.8.0" "matgl==1.3.0" "numpy<2" \
    "lightning<=2.6.0.dev20250810" "torch-geometric>=2.6.1" h5py pandas \
    "ase==3.25.0" "pymatgen==2025.6.14" $INDEXES
  uv pip freeze > env/requirements.lock.txt
fi
python -c "import torch, dgl, matgl, ase, pymatgen.core; import matgl.ext.ase; print(torch.__version__, dgl.__version__, matgl.__version__, ase.__version__, torch.cuda.is_available())"
