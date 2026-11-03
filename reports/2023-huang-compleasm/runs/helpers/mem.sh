free -m | head -2; ps -eo pid,rss,etime,args --sort=-rss | head -8 | cut -c1-160; dmesg 2>/dev/null | grep -i -E "killed process|out of memory" | tail -5
