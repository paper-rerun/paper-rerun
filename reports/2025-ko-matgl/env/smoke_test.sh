source /mnt/e/Ciencia/pipeline/2025-ko-matgl/env/activate.sh
cd /mnt/e/Ciencia/pipeline/2025-ko-matgl
flock /mnt/e/Ciencia/.gpu.lock python env/smoke_test.py
