import h5py, numpy as np, sys
for f in sys.argv[1:]:
    h = h5py.File(f, "r")
    n_mol = 0; n_conf = 0; atoms = 0; species = set(); first = None
    def visit(name, obj):
        global n_mol, n_conf, atoms, first
        if isinstance(obj, h5py.Group) and "coordinates" in obj:
            n_mol += 1
            c = obj["coordinates"].shape
            n_conf += c[0]; atoms += c[0]*c[1]
            sp = obj["species"][()]
            species.update(s.decode() if isinstance(s, bytes) else str(s) for s in sp)
            if first is None:
                first = (name, {k: (obj[k].shape, obj[k].dtype) for k in obj.keys()})
    h.visititems(visit)
    print(f.split("/")[-1], "mols", n_mol, "confs", n_conf, "atoms", atoms, sorted(species))
    print("   ", first)
