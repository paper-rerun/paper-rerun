#!/bin/bash
cd /mnt/e/Ciencia/pipeline/2025-ko-matgl
~/.local/bin/uv run --no-project --with h5py --with numpy python claims_check/inv.py data/COMP6v1
