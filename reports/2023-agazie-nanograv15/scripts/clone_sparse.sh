#!/bin/bash
# Clone without blobs, and check out everything except the presampled cores (claims first)
set -e
cd /mnt/e/Ciencia/noturno/2023-agazie-nanograv15/sources
git clone --filter=blob:none --no-checkout https://github.com/nanograv/15yr_stochastic_analysis.git repo
cd repo
git sparse-checkout init --no-cone
printf '/*\n!/tutorials/presampled_cores/\n' > .git/info/sparse-checkout
git checkout
git log -1 --format='%H %ci %s'
git ls-tree -r -l HEAD | awk '{print $4, $5}'
