#!/bin/bash
cd /mnt/e/Ciencia/noturno/2024-rasp-weatherbench2
env/.venv/bin/python -I runs/scripts/crosscheck.py 2>&1 | grep -v Warning | tee runs/logs/crosscheck.log
