#!/bin/bash
source /mnt/e/Ciencia/noturno/2022-brout-pantheonplus/env/activate.sh
cd runs
nice -n 19 python check_inputs.py
