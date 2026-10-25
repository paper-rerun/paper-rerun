source /mnt/e/Ciencia/pipeline/2025-ko-matgl/env/activate.sh
cd /mnt/e/Ciencia/pipeline/2025-ko-matgl/exec/comp6-so3net
python -W ignore score.py 2>&1 | tee score.log
