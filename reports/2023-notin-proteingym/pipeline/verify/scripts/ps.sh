#!/bin/bash
ps -eo pid,etime,pcpu,rss,args | grep -E 'run_scores|flock' | grep -v grep | cut -c1-200
nvidia-smi --query-gpu=memory.used,utilization.gpu --format=csv,noheader
