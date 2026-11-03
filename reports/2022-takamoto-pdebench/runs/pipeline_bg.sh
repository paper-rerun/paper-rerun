#!/bin/bash
cd /mnt/e/Ciencia/noturno/2022-takamoto-pdebench
env/.venv/bin/python runs/pipeline.py >> runs/pipeline.log 2>&1
echo "exit $?" >> runs/pipeline.log
