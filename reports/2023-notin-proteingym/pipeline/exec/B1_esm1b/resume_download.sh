#!/bin/bash
# Resume one download of download_data.sh (WSL restart at ~11:39 killed the first curl). The lock stops two copies writing the same file
# Usage: resume_download.sh <name glob> <lock name>
W=/mnt/e/Ciencia/pipeline/2023-notin-proteingym
flock -n "$W/data/.download_$2.lock" bash "$W/download_data.sh" "$1" || echo "another download of $1 holds the lock"
