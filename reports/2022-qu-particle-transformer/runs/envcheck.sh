#!/bin/bash
cd /mnt/e/Ciencia/noturno/2022-qu-particle-transformer/env
.venv/bin/python -c "import torch,numpy,uproot,awkward,sklearn,weaver;print('torch',torch.__version__,'cuda',torch.cuda.is_available(),torch.version.cuda,'numpy',numpy.__version__,'uproot',uproot.__version__,'awkward',awkward.__version__,'sklearn',sklearn.__version__)"; echo exit $?
nvidia-smi --query-gpu=name,memory.used,memory.total,utilization.gpu --format=csv
