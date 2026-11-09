#!/bin/bash
cd /mnt/e/Ciencia/noturno/2023-agazie-nanograv15/sources/repo
git log -1 --format='%H %ci %s'
# Which blobs are present locally (missing ones print with ?)
git ls-tree -r HEAD --name-only | grep presampled
git rev-list --objects --missing=print HEAD | grep '^?' | wc -l
du -sh .git
find tutorials -maxdepth 2 | head -40
