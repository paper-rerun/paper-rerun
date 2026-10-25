source /mnt/e/Ciencia/pipeline/2025-ko-matgl/env/activate.sh
cd /mnt/e/Ciencia/pipeline/2025-ko-matgl/exec/comp6-m3gnet
flock /mnt/e/Ciencia/.gpu.lock python -W ignore batched.py 2>&1 | tee batched.log
