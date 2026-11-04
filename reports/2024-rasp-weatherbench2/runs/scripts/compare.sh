#!/bin/bash
cd /mnt/e/Ciencia/noturno/2024-rasp-weatherbench2
env/.venv/bin/python -I runs/scripts/compare.py | tee runs/logs/compare.log
