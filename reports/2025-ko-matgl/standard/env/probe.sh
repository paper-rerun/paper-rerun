#!/bin/bash
nvidia-smi --query-gpu=name,memory.used,memory.total --format=csv
~/.local/bin/uv --version
python3 --version
df -h /mnt/e | tail -1
nproc; free -g | head -2
