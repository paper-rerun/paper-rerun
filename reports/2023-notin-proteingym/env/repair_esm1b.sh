#!/bin/bash
# esm1b_t33_650M_UR50S.pt differs from the server at byte 1,506,803,713 (bad pages from the power cut,
# inside the first 1.63 GB written before it). Re-fetch 1.40-1.70 GB, patch in place, then compare the
# whole file against the server
set -e
W=/mnt/e/Ciencia/meio/2023-notin-proteingym/data/weights
U=https://dl.fbaipublicfiles.com/fair-esm/models/esm1b_t33_650M_UR50S.pt
START=1400000000
END=1700000000
curl -sS -r $START-$END -o $W/range.bin $U
dd if=$W/range.bin of=$W/esm1b_t33_650M_UR50S.pt bs=1M seek=$START oflag=seek_bytes conv=notrunc status=none
mv $W/range.bin /tmp/esm1b_range.bin
curl -sS $U | cmp - $W/esm1b_t33_650M_UR50S.pt && echo "SAME whole esm1b_t33_650M_UR50S.pt"
cd $W && sha256sum *.pt > SHA256SUMS && cat SHA256SUMS
