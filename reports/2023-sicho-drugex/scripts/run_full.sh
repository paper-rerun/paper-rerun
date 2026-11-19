#!/bin/sh
# The two target runs, one process at a time. Peak of the pilot was 386 MB, so there is no
# need for a memory cap here, but they still do not run in parallel: the batch loop is
# already using every thread we gave it.
set -e
cd "$(dirname "$0")/.."
PY=./env/venv/Scripts/python.exe
export DRUGEX_THREADS=4

echo "=== ChEMBL 27 LSTM, n=100000, batch 600 ==="
$PY -P scripts/03_sample.py \
	data/chembl27/chembl_27_v2_smiles_rnn_PT.pkg \
	data/chembl27/chembl_27_v2_smiles_rnn_PT.vocab \
	lstm 100000 600 runs/out/full_c27.json runs/out/full_c27_smiles.txt.gz

echo "=== ChEMBL 31 GRU, n=100000, batch 600 ==="
$PY -P scripts/03_sample.py \
	data/chembl31/chembl_31_smiles_rnn_GRU_PT.pkg \
	data/chembl31/chembl_31_smiles_rnn_GRU_PT.vocab \
	gru 100000 600 runs/out/full_c31.json runs/out/full_c31_smiles.txt.gz
