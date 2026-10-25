source /mnt/e/Ciencia/noturno/2025-ko-matgl/env/activate.sh
sha256sum -c <(echo "80c8c13e2010436c052516ba3a5ab73a867a46ba3c5d4cca31d10eb2bc9d2990  claims.json")
python -I runs/scripts/score.py runs/out_main claims.json runs/results_main
