#!/bin/bash
# Stream afdb_scaling/pdbs.tar.gz out of the Zenodo tarball (no 4 GB temp file) and keep our members' v4 PDBs
set -e
ROOT=/mnt/e/Ciencia/noturno/2026-gilchrist-foldmason
HERE=$ROOT/runs/v4_vs_v6
nice -n 19 tar -xzOf "$ROOT/data/zenodo/foldmason_data.tar.gz" afdb_scaling/pdbs.tar.gz |
	nice -n 19 python3 -I "$HERE/compare_v4_v6.py" scan /dev/stdin "$ROOT/data/afdb_clusters" "$HERE"
