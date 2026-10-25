# Show dataset keys and the level-of-theory field in two files
import h5py, sys
for fn in sys.argv[1:]:
    with h5py.File(fn, "r") as f:
        g = []
        f.visititems(lambda n, o: g.append((n, o)) if isinstance(o, h5py.Group) and "coordinates" in o else None)
        n, o = g[0]
        print(fn, n, {k: (o[k].shape, str(o[k].dtype)) for k in o}, o["lot"][()] if "lot" in o else None, dict(o.attrs))
