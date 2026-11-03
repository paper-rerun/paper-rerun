cd /mnt/e/Ciencia/noturno/2022-takamoto-pdebench/scratch
df -B1 /mnt/e | tail -1; truncate -s 4G sp.test; sync; du -B1 sp.test; df -B1 /mnt/e | tail -1; rm sp.test
