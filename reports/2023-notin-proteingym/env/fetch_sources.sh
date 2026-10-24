#!/bin/bash
set -e
W=/mnt/e/Ciencia/meio/2023-notin-proteingym
cd $W
[ -d repo ] || git clone https://github.com/OATML-Markslab/ProteinGym repo
cd repo && git fetch --tags && git checkout -q PG_v1.3 && git rev-parse HEAD && git describe --tags && cd ..
B=https://marks.hms.harvard.edu/proteingym/ProteinGym_v1.3
mkdir -p sources data
for f in DMS_ProteinGym_substitutions.zip zero_shot_substitutions_scores.zip; do
  wget -q -c -O sources/$f $B/$f
done
ls -la sources
