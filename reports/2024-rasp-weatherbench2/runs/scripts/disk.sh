#!/bin/bash
cd /mnt/e/Ciencia/noturno/2024-rasp-weatherbench2
echo "$(date -Is) free on E: $(df -BG --output=avail /mnt/e | tail -1 | tr -dc 0-9) GB; data/ holds $(du -sb data | cut -f1) bytes" | tee -a runs/logs/disk_after_cleanup.log
