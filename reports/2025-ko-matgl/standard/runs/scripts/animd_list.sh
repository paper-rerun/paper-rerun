source /mnt/e/Ciencia/noturno/2025-ko-matgl/env/activate.sh
python -I - <<'P'
import h5py
h=h5py.File("data/COMP6/COMP6v1/ANI-MD/ani_md_bench.h5","r")
def v(n,o):
    if isinstance(o,h5py.Group) and "coordinates" in o: print(n, o["coordinates"].shape)
h.visititems(v)
P
