#!/bin/bash
set -eu
D=/mnt/e/Ciencia/noturno/2025-kovacs-maceoff-cego/data/test
mkdir -p $D && cd $D
curl -sSL -o test_large_neut_all.tar.gz https://api.repository.cam.ac.uk/server/api/core/bitstreams/cb8351dd-f09c-413f-921c-67a702a7f0c5/content
ls -l
md5sum test_large_neut_all.tar.gz
echo "expected md5 bf1f7c7ff1714e6ac6af2cdc642a130a"
sha256sum test_large_neut_all.tar.gz
tar tzvf test_large_neut_all.tar.gz
mkdir -p x && tar xzf test_large_neut_all.tar.gz -C x
find x -type f -exec ls -l {} \; -exec sha256sum {} \;
