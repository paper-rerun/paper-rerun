#!/bin/bash
# Exit when no run_pp.py process is left
while [ "$(pgrep -f run_pp.py | wc -l)" -gt 0 ]; do sleep 60; done
date; echo ALL_RUNS_ENDED
