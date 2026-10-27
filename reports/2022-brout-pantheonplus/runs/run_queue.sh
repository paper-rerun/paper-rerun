#!/bin/bash
# Runs the listed fits with at most 4 at a time (1 thread each = 4 threads total). Finished runs are skipped by run_fit.py
cd /mnt/e/Ciencia/noturno/2022-brout-pantheonplus/runs
printf '%s\n' "$@" | xargs -P "${NPAR:-4}" -I{} bash run_one.sh {}
echo "queue finished: $*" >> logs/queue_status.txt
