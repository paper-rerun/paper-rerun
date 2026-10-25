# Full blind run, restartable (finished npz files are skipped). SO3Net gets edge-capped batches, see predict.py
source /mnt/e/Ciencia/pipeline/2025-ko-matgl/verify/env_activate.sh
flock /mnt/e/Ciencia/.gpu.lock python predict.py --models SO3Net --batch-edges 10000 2>&1 | grep -v -e Warning -e torch.load
flock /mnt/e/Ciencia/.gpu.lock python predict.py --models M3GNet TensorNet 2>&1 | grep -v -e Warning -e torch.load
echo ALL DONE
