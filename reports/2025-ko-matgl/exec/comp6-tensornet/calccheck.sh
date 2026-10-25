source /mnt/e/Ciencia/pipeline/2025-ko-matgl/env/activate.sh
cd /mnt/e/Ciencia/pipeline/2025-ko-matgl/exec/comp6-tensornet
python -W ignore calccheck.py 2>&1 | tee calccheck.log
