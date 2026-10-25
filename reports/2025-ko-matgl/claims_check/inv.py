# Independent inventory of the 11 COMP6 v1 files
import h5py, numpy as np, glob, sys, os
root = sys.argv[1]
tot = 0
for fn in sorted(glob.glob(os.path.join(root, "*", "*.h5"))):
    nconf = 0; nmol = 0; nat = []; heavy = set(); elems = set(); nan = 0; fmax = 0.0; emin = 1e9; emax = -1e9
    names = []
    with h5py.File(fn, "r") as f:
        def visit(name, obj):
            global nconf
        groups = []
        f.visititems(lambda n, o: groups.append((n, o)) if isinstance(o, h5py.Group) and "coordinates" in o else None)
        for n, g in groups:
            sp = [s.decode() if isinstance(s, bytes) else str(s) for s in g["species"][()]]
            E = g["energies"][()]; F = g["forces"][()] if "forces" in g else None
            c = E.shape[0]; nconf += c; nmol += 1; nat.append(len(sp))
            heavy.add(sum(1 for s in sp if s != "H")); elems |= set(sp)
            nan += int(np.isnan(E).sum()) + (int(np.isnan(F).sum()) if F is not None else 0)
            if F is None: print("NOFORCES", n)
            else: fmax = max(fmax, float(np.abs(F).max()))
            emin = min(emin, float(E.min())); emax = max(emax, float(E.max()))
            if "ani_md" in fn: names.append((n, len(sp), c, sum(1 for s in sp if s != "H")))
    tot += nconf
    print(os.path.relpath(fn, root), "mol", nmol, "conf", nconf, "atoms", min(nat), max(nat), "heavy", sorted(heavy)[:3], sorted(heavy)[-3:], "elems", sorted(elems), "nan", nan, "|F|max", round(fmax, 4), "E", round(emin, 2), round(emax, 2))
    for x in names: print("   ", x)
print("TOTAL", tot)
