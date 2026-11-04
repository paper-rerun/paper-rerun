#!/bin/bash
free -g; nproc; uptime; ps -eo pid,etime,pcpu,rss,args --sort=-rss | head -8; df -BG --output=avail /mnt/e | tail -1
