"""Count how many context atoms survive the installed parse_PDB, on one metal case.

The claim conditions say to measure this instead of assuming: reading (3) of
'context_atoms_ligand' predicts every two-letter element symbol (Zn, Fe, ...) is
mapped to 0 and dropped. Check it on the real code before scoring 83 structures.
"""

import sys
import numpy as np
from collections import Counter
import prody

sys.path.insert(0, "/mnt/e/Ciencia/pipeline/2025-dauparas-ligandmpnn/repo")
from data_utils import parse_PDB, element_dict_rev

pdb = sys.argv[1]

atoms = prody.parsePDB(pdb)
other = atoms.select("not protein and not water")
raw = Counter(other.getElements())

out, backbone, other_atoms, icodes, water = parse_PDB(pdb, device="cpu", parse_all_atoms=True)
Y_t = out["Y_t"].numpy()
kept = Counter(element_dict_rev[int(t)] for t in Y_t)

print("file:", pdb)
print("non-protein non-water atoms in file:", len(other))
print("  by element:", dict(sorted(raw.items())))
print("context atoms kept by parse_PDB:", len(Y_t))
print("  by element:", dict(sorted(kept.items())))
print("residues parsed:", out["X"].shape[0])

# The point of the check: do the metals reach the model?
metals = {"ZN", "FE", "MG", "CA", "MN", "CU", "NI", "CO", "CD", "HG", "NA", "K"}
raw_metal = sum(v for k, v in raw.items() if k.upper() in metals)
kept_metal = sum(v for k, v in kept.items() if k.upper() in metals)
print("metal-ish atoms in file: %d, kept: %d" % (raw_metal, kept_metal))
