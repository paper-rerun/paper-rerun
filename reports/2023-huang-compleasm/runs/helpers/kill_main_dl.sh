# Stops only this project's main download.sh and its human-genome curl (duplicate of the prefetch)
for p in $(pgrep -f "bash /mnt/e/Ciencia/noturno/2023-huang-compleasm/data/download.sh"); do kill $p; done
kill 30111
sleep 1
ps -eo pid,args | grep "2023-huang-compleasm" | grep -E "curl|download" | grep -v grep | cut -c1-150
