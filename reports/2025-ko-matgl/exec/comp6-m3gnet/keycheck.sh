source /mnt/e/Ciencia/pipeline/2025-ko-matgl/env/activate.sh
cd /mnt/e/Ciencia/pipeline/2025-ko-matgl/exec/comp6-m3gnet
export CUDA_VISIBLE_DEVICES= MPLBACKEND=Agg
python -W ignore keycheck.py 2>&1 | tee keycheck.log
