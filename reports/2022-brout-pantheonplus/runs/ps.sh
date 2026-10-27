#!/bin/bash
ps -eo pid,ni,pcpu,etime,rss,args | grep -E 'run_fit|xargs' | grep -v grep
uptime
