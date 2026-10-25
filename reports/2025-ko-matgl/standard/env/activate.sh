# Source before every run
cd /mnt/e/Ciencia/noturno/2025-ko-matgl
source env/.venv/bin/activate
export MPLBACKEND=Agg
export MATGL_CACHE=/mnt/e/Ciencia/noturno/2025-ko-matgl/data/matgl_cache
export DGLBACKEND=pytorch
export OMP_NUM_THREADS=4 MKL_NUM_THREADS=4 OPENBLAS_NUM_THREADS=4
unset DISPLAY WAYLAND_DISPLAY
