#!/bin/bash
set -euo pipefail
cd "$(dirname "$0")/.."
./env/venv/bin/python -I -c "
import torch, mace, ase, numpy, e3nn
print('torch', torch.__version__, torch.version.cuda, torch.cuda.is_available())
print('mace', mace.__version__, 'ase', ase.__version__, 'numpy', numpy.__version__, 'e3nn', e3nn.__version__)
print(torch.cuda.get_device_name(0))
print('free/total GB', [x/2**30 for x in torch.cuda.mem_get_info()])
"
uv pip freeze --python ./env/venv/bin/python > env/requirements.freeze.txt
wc -l env/requirements.freeze.txt
