#!/bin/bash
# Build the environment: FoldMason release 4-dd3c235 prebuilt binary (linux-avx2) from the authors' GitHub release
# t-coffee (apt) is only needed for the HOMSTRAD SP scores and is installed separately if HOMSTRAD is available
set -e
ROOT=/mnt/e/Ciencia/noturno/2026-gilchrist-foldmason
mkdir -p "$ROOT/env/bin_dl"
cd "$ROOT/env/bin_dl"
URL=https://github.com/steineggerlab/foldmason/releases/download/4-dd3c235/foldmason-linux-avx2.tar.gz
if [ ! -s foldmason-linux-avx2.tar.gz ]; then
	curl -sSL -o foldmason-linux-avx2.tar.gz "$URL"
fi
SIZE=$(stat -c %s foldmason-linux-avx2.tar.gz)
echo "size $SIZE (expected 53805347 from server Content-Length)"
[ "$SIZE" = 53805347 ]
sha256sum foldmason-linux-avx2.tar.gz
rm -rf "$ROOT/env/foldmason"
tar -xzf foldmason-linux-avx2.tar.gz -C "$ROOT/env"
ls -la "$ROOT/env/foldmason/bin"
