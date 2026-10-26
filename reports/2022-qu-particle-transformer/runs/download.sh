#!/bin/bash
# Download JetClass test tar, resumable (-c), then verify size and md5
set -u
D=/mnt/e/Ciencia/noturno/2022-qu-particle-transformer/data
cd "$D"
URL=https://zenodo.org/records/6619768/files/JetClass_Pythia_test_20M.tar
aria2c -c -x16 -s16 -k 64M --file-allocation=none --summary-interval=300 --console-log-level=warn \
  --max-tries=0 --retry-wait=10 -o JetClass_Pythia_test_20M.tar "$URL"
echo "aria2c exit $?"
SIZE=$(stat -c %s JetClass_Pythia_test_20M.tar)
echo "size $SIZE (expected 30370816000)"
md5sum JetClass_Pythia_test_20M.tar | tee JetClass_Pythia_test_20M.tar.md5
echo "expected md5 64e5156d26d101adeb43b8388207d767"
