#!/bin/bash
# Time one raw read of the checkpoint from /mnt/e
S=$(date +%s.%N)
cat /mnt/e/Ciencia/pipeline/2023-notin-proteingym/data/weights/esm1b_t33_650M_UR50S.pt > /dev/null
echo read_seconds $(echo "$(date +%s.%N) - $S" | bc)
