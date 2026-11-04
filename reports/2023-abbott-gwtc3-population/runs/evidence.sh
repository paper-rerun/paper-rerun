#!/bin/bash
# Saves the output of the setup checks that were only printed to the terminal during the run.
# Captured during report revision (2026-11-04, after both runs finished), not at run time.
B=/mnt/e/Ciencia/noturno/2023-abbott-gwtc3-population
cd $B
{ date; bash runs/check_gpu.sh; } > runs/check_gpu.log 2>&1
{ date; bash env/test_cupy.sh; } > runs/test_cupy.log 2>&1
{ date; source env/activate.sh; python -c "import setuptools, tables, deepdish; print('setuptools', setuptools.__version__, 'tables', tables.__version__, 'deepdish ok')"; } > runs/fix_tables.log 2>&1
bash runs/sk.sh > runs/sampler_kwargs_compare.log 2>&1
echo EVIDENCE_DONE
