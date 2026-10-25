cd /mnt/e/Ciencia/pipeline/2025-ko-matgl/verify
for M in M3GNet TensorNet SO3Net; do for F in repo/pretrained_models/$M-ANI-1x-Subset-PES/*; do echo "$(git hash-object $F) $F"; done; done
for F in $(find /mnt/e/Ciencia/pipeline/2025-ko-matgl/data/COMP6v1 -name '*.h5' | sort); do echo "$(git hash-object $F) $(stat -c %s $F) $F"; done
