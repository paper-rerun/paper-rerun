# Source before every run
cd /mnt/e/Ciencia/noturno/2022-brout-pantheonplus
source env/.venv/bin/activate
export MPLBACKEND=Agg
export OMP_NUM_THREADS=4 MKL_NUM_THREADS=4 OPENBLAS_NUM_THREADS=4 NUMEXPR_NUM_THREADS=4
unset DISPLAY WAYLAND_DISPLAY
