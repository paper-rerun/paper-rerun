#!/bin/bash
# Download AFDB model_v6 PDBs for the 160 benchmark clusters, saved under the v4 name (restartable)
# First attempt with aria2c -j 4 got HTTP 429 on 191 requests, so this goes one file at a time
set -e
ROOT=/mnt/e/Ciencia/noturno/2026-gilchrist-foldmason
HERE=$ROOT/runs/afdb_download
DATA=$ROOT/data/afdb_clusters
mkdir -p "$DATA"
# Drop partial files left by the aborted aria2c run
find "$DATA" -name '*.aria2' | while read -r control
do
	rm -f "$control" "${control%.aria2}"
done
python3 -I "$HERE/make_aria_list.py" "$ROOT/sources/analysis" "$DATA" "$HERE/aria_list.txt"
nice -n 19 python3 -I "$HERE/fetch_afdb.py" "$HERE/aria_list.txt" "$HERE/sizes.tsv"
find "$DATA" -name '*.pdb' | wc -l
