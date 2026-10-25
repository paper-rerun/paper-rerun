source /mnt/e/Ciencia/noturno/2025-ko-matgl/env/activate.sh
python -I - <<'P'
import numpy as np, glob, json
for f in sorted(glob.glob("runs/out_main/*.npz")):
    if "tmp" in f: continue
    d=np.load(f)
    e=np.mean(np.abs(d["energy_pred_eV"]-d["energy_ref_eV"])/d["n_atoms"])*1000
    fm=np.mean(np.abs(d["forces_pred_eV_per_A"]-d["forces_ref_eV_per_A"]))
    print(f.split("/")[-1], len(d["n_atoms"]), round(e,3), round(float(fm),4), json.loads(str(d["meta"]))["seconds"])
P
