#!/bin/bash
W=/mnt/e/Ciencia/meio/2023-notin-proteingym
export MPLBACKEND=Agg
$W/env/.venv/bin/python $W/runs/revision_checks.py > $W/runs/logs/revision_checks.log 2>&1
echo "EXIT $?" >> $W/runs/logs/revision_checks.log
$W/env/.venv/bin/python $W/runs/check_reference_versions.py > $W/runs/logs/check_reference_versions.log 2>&1
echo "EXIT $?" >> $W/runs/logs/check_reference_versions.log
