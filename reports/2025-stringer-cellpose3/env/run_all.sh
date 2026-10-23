#!/bin/bash
# Headless run of the authors' real-data Cellpose3 analyses, one GPU job at a time
cd /mnt/e/Ciencia/artigos/2025-stringer-cellpose3
source .venv/bin/activate
export MPLBACKEND=Agg OMP_NUM_THREADS=4 MKL_NUM_THREADS=4
unset DISPLAY WAYLAND_DISPLAY
for which in "$@"; do
	/usr/bin/time -v flock /mnt/e/Ciencia/.gpu.lock python run_real.py "$which" > "logs/$which.log" 2>&1
	echo "EXIT $?" >> "logs/$which.log"
done
