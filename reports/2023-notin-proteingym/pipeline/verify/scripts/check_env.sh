#!/bin/bash
W=/mnt/e/Ciencia/pipeline/2023-notin-proteingym
E=$W/verify/env
cmp "$E/freeze.txt" "$W/env/freeze.txt" && echo "freeze identical to env/freeze.txt"
sha256sum "$W/env/requirements.lock"
"$E/venv/bin/python" -c "import torch, numpy, pandas, scipy, sklearn, Bio, numba; print('torch', torch.__version__, 'cuda', torch.version.cuda, 'gpu', torch.cuda.is_available())"
nvidia-smi --query-gpu=name,memory.used,memory.total,utilization.gpu --format=csv
ps aux | grep -E 'compute_fitness|python' | grep -v grep | head
