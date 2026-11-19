set -e
cd /e/Ciencia/noturno/2023-sicho-drugex-cego
PY=.venv/Scripts/python.exe
nice -n 19 $PY -P scripts/sample_rnn.py --pkg downloads/models/ex27/chembl_27_v2_smiles_rnn_PT.pkg \
  --vocab downloads/models/ex27/chembl_27_v2_smiles_rnn_PT.vocab --arch lstm \
  --num 100000 --batch-size 600 --seed 1 --threads 4 --out runs/full_chembl27_lstm.smi
nice -n 19 $PY -P scripts/score_sample.py runs/full_chembl27_lstm.smi
nice -n 19 $PY -P scripts/sample_rnn.py --pkg downloads/models/ex31/chembl_31_smiles_rnn_GRU_PT.pkg \
  --vocab downloads/models/ex31/chembl_31_smiles_rnn_GRU_PT.vocab --arch gru \
  --num 100000 --batch-size 600 --seed 1 --threads 4 --out runs/full_chembl31_gru.smi
nice -n 19 $PY -P scripts/score_sample.py runs/full_chembl31_gru.smi
echo ALL_DONE
