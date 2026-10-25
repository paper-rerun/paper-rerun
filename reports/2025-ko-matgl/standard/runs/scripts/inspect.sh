source /mnt/e/Ciencia/noturno/2025-ko-matgl/env/activate.sh
python -I runs/scripts/inspect.py $(find data/COMP6 -name '*.h5' | sort)
python - <<'P'
import matgl, inspect, matgl.ext.ase as a
print(inspect.signature(matgl.load_model))
print([n for n in dir(a) if not n.startswith('_')])
P
grep -n "class PESCalculator" -A60 env/.venv/lib/python3.11/site-packages/matgl/ext/ase.py | head -120
