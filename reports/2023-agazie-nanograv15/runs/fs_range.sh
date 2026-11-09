#!/bin/bash
W=/mnt/e/Ciencia/noturno/2023-agazie-nanograv15
cd $W/runs; nice -n 19 $W/env/venv/bin/python -I fs_range.py $W/sources/repo
