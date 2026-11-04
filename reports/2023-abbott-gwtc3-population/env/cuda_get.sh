#!/bin/bash
# Fetch CUDA 11.1 runtime libs as .deb from NVIDIA's public apt repo, check size+sha256 from the repo index, unpack locally (no system install)
set -e
cd /mnt/e/Ciencia/noturno/2023-abbott-gwtc3-population/env/cuda111/debs
R=https://developer.download.nvidia.com/compute/cuda/repos/ubuntu2004/x86_64
for f in cuda-cudart-11-1_11.1.74-1_amd64.deb cuda-nvrtc-11-1_11.1.105-1_amd64.deb cuda-nvtx-11-1_11.1.74-1_amd64.deb libcublas-11-1_11.3.0.106-1_amd64.deb libcufft-11-1_10.3.0.105-1_amd64.deb libcurand-11-1_10.2.2.105-1_amd64.deb libcusparse-11-1_11.3.0.10-1_amd64.deb libcusolver-11-1_11.0.1.105-1_amd64.deb; do
  [ -f $f ] || curl -sSL -o $f $R/$f
  exp_sha=$(grep -A12 "^Filename: ./$f$" Packages | grep -m1 '^SHA256:' | cut -d' ' -f2)
  exp_size=$(grep -B8 -A8 "^Filename: ./$f$" Packages | grep -m1 '^Size:' | cut -d' ' -f2)
  got_sha=$(sha256sum $f | cut -d' ' -f1); got_size=$(stat -c %s $f)
  [ "$got_sha" = "$exp_sha" ] && [ "$got_size" = "$exp_size" ] && echo "OK $f $got_size $got_sha" || { echo "FAIL $f size $got_size/$exp_size sha $got_sha/$exp_sha"; exit 1; }
  dpkg-deb -x $f ../root
done
find ../root -name "*.so*" | grep -E "lib(cudart|nvrtc|cublas|cufft|curand|cusparse|nvToolsExt)" | head -30
