source /mnt/e/Ciencia/pipeline/2025-ko-matgl/verify/env_activate.sh
flock /mnt/e/Ciencia/.gpu.lock python probe_mem.py "$@" 2>&1 | grep -v -e Warning -e torch.load
