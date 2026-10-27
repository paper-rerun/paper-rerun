#!/bin/bash
# List the Zenodo tarball (no extraction) and look for HOMSTRAD inputs
set -e
ROOT=/mnt/e/Ciencia/noturno/2026-gilchrist-foldmason
HERE=$ROOT/runs/zenodo_inspect
nice -n 19 tar -tzvf "$ROOT/data/zenodo/foldmason_data.tar.gz" > "$HERE/tar_listing.txt"
wc -l "$HERE/tar_listing.txt"
awk '{print $6}' "$HERE/tar_listing.txt" | awk -F/ '{print $1"/"$2}' | sort | uniq -c | sort -rn | head -40 > "$HERE/top_dirs.txt"
grep -ic homstrad "$HERE/tar_listing.txt" || true
