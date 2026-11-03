#!/bin/bash
pgrep -af "miniprot|compleasm" | cut -c1-150
free -m | head -2
ls -la /mnt/e/Ciencia/noturno/2023-huang-compleasm/runs/outs097_zmay/
