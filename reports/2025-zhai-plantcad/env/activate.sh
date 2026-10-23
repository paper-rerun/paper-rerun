# Source before every run: venv, HF cache inside the paper folder, headless matplotlib, 4 CPU threads
cd /mnt/e/Ciencia/artigos/2025-zhai-plantcad
source env/.venv/bin/activate
export HF_HOME=/mnt/e/Ciencia/artigos/2025-zhai-plantcad/hf_cache
export MPLBACKEND=Agg
export OMP_NUM_THREADS=4 MKL_NUM_THREADS=4 OPENBLAS_NUM_THREADS=4
unset DISPLAY WAYLAND_DISPLAY
