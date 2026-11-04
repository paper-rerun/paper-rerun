#!/bin/bash
# One-line status of both runs: process alive, last progress line, result file present
cd /mnt/e/Ciencia/noturno/2023-abbott-gwtc3-population/runs
for s in 101 202; do
  alive=$(pgrep -f "run_pp.py $s" | wc -l)
  last=$(tr '\r' '\n' < pp_seed$s.log | grep -E "ncall:" | tail -1 | cut -c1-120)
  res=$(ls pp_seed$s/result/*_result.json 2>/dev/null | wc -l)
  err=$(grep -cE "Traceback|MemoryError|Killed" pp_seed$s.log)
  echo "seed$s alive=$alive result=$res err=$err | $last"
done
free -g | awk '/Mem/{print "RAM used GB", $3}'
