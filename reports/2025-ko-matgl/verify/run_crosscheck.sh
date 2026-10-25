source /mnt/e/Ciencia/pipeline/2025-ko-matgl/verify/env_activate.sh
CUDA_VISIBLE_DEVICES= python crosscheck_ase.py 2>&1 | grep -v -e Warning -e torch.load
