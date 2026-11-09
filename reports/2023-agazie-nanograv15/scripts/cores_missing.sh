#!/bin/bash
cd /mnt/e/Ciencia/noturno/2023-agazie-nanograv15/sources/repo
# For each core: blob id and whether the object is present locally (no fetch)
git ls-tree HEAD tutorials/presampled_cores/ | while read m t h p; do
  if git -c core.promisor=false cat-file -e $h 2>/dev/null && git rev-list --objects --missing=print HEAD | grep -q "^?$h"; then s=missing; else s=check; fi
  echo "$h $p $(git rev-list --objects --missing=print HEAD -- | grep -c "^?$h")"
done
echo "--- history of the cores folder (commits only, no blobs)"
git log --format='%H %ci %an %s' -- tutorials/presampled_cores
echo "--- history of data_release"
git log --format='%H %ci %an %s' -- data_release | head
