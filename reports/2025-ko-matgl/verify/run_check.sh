source /mnt/e/Ciencia/pipeline/2025-ko-matgl/verify/env_activate.sh
python -c "import sys,torch,dgl,matgl;print(sys.version.split()[0],torch.__version__,torch.version.cuda,dgl.__version__,matgl.__version__,matgl.__file__,torch.cuda.get_device_name(0))"
# Weights and data integrity: git blob hashes of the model files at the tag, data blobs vs manifest
for M in M3GNet TensorNet SO3Net; do echo $M $(git -C repo rev-parse HEAD:pretrained_models/$M-ANI-1x-Subset-PES/model.pt 2>/dev/null) ; ls repo/pretrained_models/$M-ANI-1x-Subset-PES; for F in repo/pretrained_models/$M-ANI-1x-Subset-PES/*; do echo "  $F $(git hash-object $F)"; done; done
for F in $(find /mnt/e/Ciencia/pipeline/2025-ko-matgl/data/COMP6v1 -name '*.h5' | sort); do echo "$(git hash-object $F) $(stat -c %s $F) $F"; done
flock /mnt/e/Ciencia/.gpu.lock python check_sign_unit.py
