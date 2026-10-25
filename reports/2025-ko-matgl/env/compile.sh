# Regenerates env/requirements.lock.txt from requirements.in + constraints.txt (the authors' uv.lock export
# minus torch/torchdata/triton/nvidia/dgl). Only needed to rebuild the lock; setup.sh uses the lock as is.
# --no-sources: the repo pyproject pins dgl to the CPU wheel index via [tool.uv.sources]; we want the cu121 build.
set -e
ROOT=/mnt/e/Ciencia/pipeline/2025-ko-matgl
cd $ROOT
~/.local/bin/uv pip compile env/requirements.in -c env/constraints.txt \
  --python-version 3.12 --python-platform x86_64-manylinux_2_28 \
  --extra-index-url https://download.pytorch.org/whl/cu121 \
  --find-links https://data.dgl.ai/wheels/torch-2.4/cu121/repo.html \
  --index-strategy unsafe-best-match \
  --emit-index-url --emit-find-links \
  --no-emit-package matgl \
  --generate-hashes --no-sources \
  -o env/requirements.lock.txt
