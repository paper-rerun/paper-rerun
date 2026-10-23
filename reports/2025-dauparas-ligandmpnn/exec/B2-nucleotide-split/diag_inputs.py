"""Checks the two things the claim definitions told the run stage to measure, not assume:
how many MODEL records the biounit files carry, and which context atoms the installed
parse_PDB actually keeps. Nothing here touches the GPU."""

import json
import os
import sys

import numpy as np

ROOT = "/mnt/e/Ciencia/pipeline/2025-dauparas-ligandmpnn"
sys.path.insert(0, os.path.join(ROOT, "repo"))
from data_utils import parse_PDB  # noqa: E402

ids = json.load(open(os.path.join(ROOT, "repo/training/test_nucleotide.json")))
print("nucleotide ids:", len(ids))

# How many of the 74 biounit files hold more than one MODEL
multi = []
for pid in ids:
    p = os.path.join(ROOT, "data/structures/biounit1", pid + ".pdb")
    n = sum(1 for line in open(p) if line.startswith("MODEL "))
    if n > 1:
        multi.append((pid, n))
print("biounit1 files with >1 MODEL:", len(multi), multi)

# Element survival inside the authors' own parser. Reading (3) of the definition
# claims every two-letter element is dropped; check it on a metal case and a
# nucleotide case instead of trusting either reading.
ELEMENTS = [
    "H", "He", "Li", "Be", "B", "C", "N", "O", "F", "Ne", "Na", "Mg", "Al", "Si",
    "P", "S", "Cl", "Ar", "K", "Ca", "Sc", "Ti", "V", "Cr", "Mn", "Fe", "Co",
    "Ni", "Cu", "Zn",
]


def report(path, label):
    from prody import parsePDB
    atoms = parsePDB(path).select("occupancy > 0")
    other = atoms.select("not protein and not water")
    raw = 0 if other is None else other.numAtoms()
    el = {} if other is None else {}
    if other is not None:
        for e in other.getElements():
            el[e] = el.get(e, 0) + 1
    out, _bb, _oa, _ic, _w = parse_PDB(path, parse_all_atoms=True)
    kept = int(out["Y_m"].sum().item())
    print(f"{label}: residues={out['X'].shape[0]} other_atoms_raw={raw} kept_by_parse_PDB={kept}")
    print(f"   elements in other_atoms: {sorted(el.items())}")
    heavy = sum(v for k, v in el.items() if k.upper() != "H")
    print(f"   heavy (non-H) other_atoms: {heavy}  -> kept == heavy ? {kept == heavy}")
    return out


first_nuc = ids[0]
report(os.path.join(ROOT, "data/structures/biounit1", first_nuc + ".pdb"), f"{first_nuc} biounit1")
report(os.path.join(ROOT, "data/structures/asym", first_nuc + ".pdb"), f"{first_nuc} asym")

metal = json.load(open(os.path.join(ROOT, "repo/training/test_metal.json")))[0]
report(os.path.join(ROOT, "data/structures/biounit1", metal + ".pdb"), f"{metal} biounit1 (metal case)")
