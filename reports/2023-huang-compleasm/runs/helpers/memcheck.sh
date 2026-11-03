#!/bin/bash
free -m
nproc
uptime
ps aux --sort=-rss | head -8 | cut -c1-200
