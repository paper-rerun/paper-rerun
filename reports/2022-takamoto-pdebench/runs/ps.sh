ps -eo pid,etime,pcpu,rss,args | grep -E 'tar|cp |md5sum|curl|python|pipeline|download' | grep -v grep | cut -c1-200
ls -la /mnt/e/Ciencia/noturno/2022-takamoto-pdebench/runs/eval 2>/dev/null | head -40
grep MemAvailable /proc/meminfo
