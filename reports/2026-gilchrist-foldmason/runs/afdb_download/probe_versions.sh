#!/bin/bash
HERE=/mnt/e/Ciencia/noturno/2026-gilchrist-foldmason/runs/afdb_download
nice -n 19 python3 -I "$HERE/probe_versions.py" "$HERE/missing_status.tsv" "$HERE/probe_versions.tsv" > "$HERE/probe_versions.log" 2>&1
