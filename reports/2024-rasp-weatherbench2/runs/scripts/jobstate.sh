#!/bin/bash
ps -eo pid,etime,pcpu,rss,nlwp,args | grep [e]valuate.py | cut -c1-120
grep -v "Metadata\|Authentication" /mnt/e/Ciencia/noturno/2024-rasp-weatherbench2/runs/logs/official_subset_graphcast.log | tail -4 | cut -c1-200
