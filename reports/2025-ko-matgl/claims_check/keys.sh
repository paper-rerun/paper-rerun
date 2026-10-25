#!/bin/bash
cd /mnt/e/Ciencia/pipeline/2025-ko-matgl
~/.local/bin/uv run --no-project --with h5py --with numpy python claims_check/keys.py data/COMP6v1/ANI-MD/ani_md_bench.h5 data/COMP6v1/s66x8/s66x8_wb97x6-31gd.h5 data/COMP6v1/GDB10to13/gdb13_13_test1000.h5
