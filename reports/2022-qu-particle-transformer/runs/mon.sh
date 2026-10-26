#!/bin/bash
nvidia-smi --query-gpu=utilization.gpu,memory.used --format=csv
ps -eo pid,pcpu,rss,etime,args --sort=-pcpu | grep -v grep | grep -E "weaver|python" | head
sleep 3
nvidia-smi --query-gpu=utilization.gpu,memory.used --format=csv,noheader
nvidia-smi --query-compute-apps=pid,used_memory --format=csv
