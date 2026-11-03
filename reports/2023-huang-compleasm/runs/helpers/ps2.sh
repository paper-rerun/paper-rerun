ps -eo pid,etime,rss,args | grep "2023-huang-compleasm" | grep -E "curl|miniprot" | grep -v grep | cut -c1-200; free -g | head -2
