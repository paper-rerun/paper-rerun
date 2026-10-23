#!/bin/bash
# Download train/valid in full and stream-sample the test sets
set -uo pipefail
cd /mnt/e/Ciencia/artigos/2025-zhai-plantcad/data
B=https://huggingface.co/datasets/kuleshov-group/cross-species-single-nucleotide-annotation/resolve/main
for T in TIS Donor; do mkdir -p $T; for S in train valid; do curl -sL -o $T/$S.tsv $B/$T/$S.tsv; done; done
S=../scripts/stream_sample.py
python3 $S TIS/test_sorghum.tsv 0.20 TIS/test_sorghum.sample.tsv &
python3 $S Donor/test_sorghum.tsv 0.05 Donor/test_sorghum.sample.tsv &
python3 $S TIS/test_maize.tsv 0.05 TIS/test_maize.sample.tsv &
python3 $S Donor/test_maize.tsv 0.02 Donor/test_maize.sample.tsv &
wait
wc -l */*.tsv
