#!/bin/bash
cd /mnt/e/Ciencia/noturno/2022-takamoto-pdebench
bash runs/download.sh >> runs/download.log 2>&1
echo "exit $?" >> runs/download.log
