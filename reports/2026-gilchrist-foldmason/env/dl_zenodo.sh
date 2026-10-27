#!/bin/bash
# Download the authors' Zenodo data tarball (restartable) and check md5
set -e
D=/mnt/e/Ciencia/noturno/2026-gilchrist-foldmason/data/zenodo
mkdir -p "$D"; cd "$D"
nice -n 19 aria2c -c -x 4 -s 4 --file-allocation=none --summary-interval=60 \
  -o foldmason_data.tar.gz "https://zenodo.org/api/records/17311030/files/foldmason_data.tar.gz/content"
stat -c %s foldmason_data.tar.gz
nice -n 19 md5sum foldmason_data.tar.gz | tee foldmason_data.tar.gz.md5
