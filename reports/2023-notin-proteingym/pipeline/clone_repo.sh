#!/bin/bash
set -eu
W=/mnt/e/Ciencia/pipeline/2023-notin-proteingym
cd "$W"
if [ ! -d repo/.git ]; then
  git clone https://github.com/OATML-Markslab/ProteinGym repo
fi
cd repo
git fetch --tags -q
git checkout -q PG_v1.3
git rev-parse HEAD
git log -1 --format='%H %ci %s'
ls
nvidia-smi --query-gpu=name,memory.total,memory.used,driver_version --format=csv
python3 --version; ~/.local/bin/uv --version
df -h /mnt/e | tail -1
