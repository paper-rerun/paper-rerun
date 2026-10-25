source /mnt/e/Ciencia/noturno/2025-ko-matgl/env/activate.sh
python -I - <<'P'
import numpy as np, glob, json
tot={}
n=0
for f in glob.glob("runs/out_main/*.npz"):
    m=json.loads(str(np.load(f)["meta"])); tot[m["model"]]=tot.get(m["model"],0)+m["seconds"]; n+=len(np.load(f)["n_atoms"])
print({k:round(v/3600,2) for k,v in tot.items()}, "conformation-model pairs", n)
P
