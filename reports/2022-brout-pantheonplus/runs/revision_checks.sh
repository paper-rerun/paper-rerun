#!/bin/bash
# Checks added in the report revision; light mode (nice 19, 4 threads)
cd /mnt/e/Ciencia/noturno/2022-brout-pantheonplus
source env/activate.sh
cd runs
nice -n 19 python selftest_all_rows.py > logs/selftest_all_rows.log 2>&1; echo "selftest exit $?"
nice -n 19 python released_like_near_bestfit.py > logs/released_like_near_bestfit.log 2>&1; echo "near exit $?"
