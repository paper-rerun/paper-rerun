#!/bin/bash
cd /mnt/e/Ciencia/noturno/2023-agazie-nanograv15/sources/repo
du -sh .git
git rev-list --objects --missing=print HEAD > /tmp/ng15_missing.txt
grep -c '^?' /tmp/ng15_missing.txt
for h in $(git ls-tree HEAD tutorials/presampled_cores/ | awk '{print $3}'); do grep -q "^?$h" /tmp/ng15_missing.txt && echo "$h missing" || echo "$h PRESENT"; done
rm /tmp/ng15_missing.txt
