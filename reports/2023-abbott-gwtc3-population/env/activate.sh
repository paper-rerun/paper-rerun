# Source this in WSL: puts the local CUDA 11.1 runtime libs and the venv on the path
E=/mnt/e/Ciencia/noturno/2023-abbott-gwtc3-population/env
export CUDA_PATH=$E/cuda111/root/usr/local/cuda-11.1
export LD_LIBRARY_PATH=/usr/lib/wsl/lib:$CUDA_PATH/targets/x86_64-linux/lib
export CUPY_CACHE_DIR=$E/cupy_cache
export MPLBACKEND=Agg OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1
export PATH=$E/venv/bin:$HOME/.local/bin:$PATH
