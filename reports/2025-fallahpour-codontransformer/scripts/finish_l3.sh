#!/bin/bash
# Wait for the primary generation run, then score it, then run the secondary E. coli
# organism token (pre-registered as a secondary analysis) and score that too.
export PATH="$HOME/.local/bin:$PATH"
ROOT=/mnt/e/Ciencia/noturno/2025-fallahpour-codontransformer
cd "$ROOT"
PY="env/.venv/bin/python -I -u"
export OMP_NUM_THREADS=4 MKL_NUM_THREADS=4

until grep -qE "^done in|^STOP:" runs/logs/generate_primary.log; do sleep 20; done
echo "primary generation finished"

nice -n 19 $PY scripts/compare_l3.py runs/out/generated_primary.csv \
  > runs/logs/compare_l3_primary.log 2>&1

nice -n 19 $PY scripts/generate_sequences.py runs/out/generated_ecoli_mg1655.csv \
  --ecoli-token "Escherichia coli str. K-12 substr. MG1655" \
  --only-organism "Escherichia coli" > runs/logs/generate_ecoli_mg1655.log 2>&1

nice -n 19 $PY scripts/compare_l3.py runs/out/generated_ecoli_mg1655.csv \
  > runs/logs/compare_l3_mg1655.log 2>&1

echo "ALL DONE"
