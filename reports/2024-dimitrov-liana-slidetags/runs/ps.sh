ps -eo pid,ni,pcpu,rss,etime,args --sort=-pcpu | grep -E "python|PID" | head -8
