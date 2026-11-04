#!/bin/bash
# Block up to ~9.5 min; return early if any run ends (process gone)
cd /mnt/e/Ciencia/noturno/2023-abbott-gwtc3-population/runs
for i in $(seq 1 50); do
  n=$(pgrep -f "run_pp.py" | wc -l)
  [ "$n" -lt 2 ] && break
  sleep 10
done
date; bash status.sh; ls -la --time-style=+%H:%M pp_seed*/result 2>/dev/null | grep -v "^total"
