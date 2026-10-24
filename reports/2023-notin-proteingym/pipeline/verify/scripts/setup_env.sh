#!/bin/bash
# Rebuild the venv from scratch in verify/env from the frozen lockfile (same steps as env/setup_env.sh, other folder)
set -eu
W=/mnt/e/Ciencia/pipeline/2023-notin-proteingym
E=$W/verify/env
UV=~/.local/bin/uv
export UV_LINK_MODE=copy
rm -rf "$E/venv"
$UV venv --python 3.10.14 "$E/venv"
$UV pip sync --python "$E/venv/bin/python" --require-hashes "$W/env/requirements.lock"
$UV pip freeze --python "$E/venv/bin/python" > "$E/freeze.txt"
diff "$E/freeze.txt" "$W/env/freeze.txt" && echo "freeze identical to env/freeze.txt"
sha256sum "$W/env/requirements.lock"
"$E/venv/bin/python" -c "import torch, numpy, pandas, scipy, sklearn, Bio, numba; print('torch', torch.__version__, 'cuda', torch.version.cuda, 'gpu', torch.cuda.is_available())"
nvidia-smi --query-gpu=name,memory.used,memory.total,utilization.gpu --format=csv
