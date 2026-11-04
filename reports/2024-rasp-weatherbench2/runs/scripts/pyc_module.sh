#!/bin/bash
cd /mnt/e/Ciencia/noturno/2024-rasp-weatherbench2
env/.venv/bin/python -I runs/scripts/pyc_module.py 2>&1 | tee -a runs/logs/pyc_diff.log
