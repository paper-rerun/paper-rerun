"""Self-check for the scoring masks, before they are used on 474 structures.

Four things worth catching early: that the residue count matches what the
authors' own parser produces (otherwise every recovery is scored at shifted
positions), that glycine never gets into the side-chain reading, that the
any-atom set always contains the side-chain set, and that a hand-computed
distance agrees with the KD-tree answer on one small case.
"""

import os
import sys

sys.path.insert(0, "/mnt/e/Ciencia/pipeline/2025-dauparas-ligandmpnn/verify/repo")
sys.path.insert(0, "/mnt/e/Ciencia/pipeline/2025-dauparas-ligandmpnn/verify/tools")

import numpy as np
from prody import confProDy, parsePDB

import data_utils
from score_recovery import BACKBONE, CUTOFF, masks_for

confProDy(verbosity="critical")

ROOT = "/mnt/e/Ciencia/pipeline/2025-dauparas-ligandmpnn"
CASES = [
    ROOT + "/verify/inputs/small_molecule/1a28_ASTR.pdb",
    ROOT + "/verify/inputs/small_molecule/1bzc_ATPI.pdb",
    ROOT + "/data/structures/asym/1a0a.pdb",            # nucleotide
    ROOT + "/data/structures/asym/1dwh.pdb",            # metal
    ROOT + "/verify/inputs/fixed/asym/5l70.pdb",        # the repaired entry
]

for path in CASES:
    masks, info = masks_for(path)

    out, _, _, _, _ = data_utils.parse_PDB(path, device="cpu")
    n_theirs = int(out["S"].shape[0])
    assert len(masks["any_atom|all"]) == n_theirs, \
        "%s: mine %d, theirs %d" % (path, len(masks["any_atom|all"]), n_theirs)

    atoms = parsePDB(path).select("occupancy > 0").select("protein")
    resnames = np.array(atoms.select("name CA").getResnames())
    n_gly = int((masks["sidechain|all"] & (resnames == "GLY")).sum())
    assert n_gly == 0, "%s: %d glycines in the side-chain set" % (path, n_gly)

    assert (masks["sidechain|all"] <= masks["any_atom|all"]).all(), \
        "%s: side-chain set is not inside the any-atom set" % path
    assert (masks["any_atom|metal_transition"] <= masks["any_atom|all"]).all(), \
        "%s: metal context set is not inside the all-context set" % path

    print("%-26s res=%-5d any=%-5d sc=%-5d metal=%-4d ctx_all=%-6d ctx_metal=%d"
          % (os.path.basename(path), len(masks["any_atom|all"]),
             int(masks["any_atom|all"].sum()), int(masks["sidechain|all"].sum()),
             int(masks["any_atom|metal_transition"].sum()),
             info["n_context_all"], info["n_context_metal"]))

# brute force, no KD-tree, on the smallest case
path = CASES[0]
masks, _ = masks_for(path)
atoms = parsePDB(path).select("occupancy > 0")
protein = atoms.select("protein")
other = atoms.select("not protein and not water")
oth = np.asarray(other.getCoords(), float)[
    ~np.isin([str(e).strip().upper() for e in other.getElements()], ["H", "D"])]
ca = protein.select("name CA")
keys = list(zip(ca.getChids(), ca.getResnums(), [str(i) for i in ca.getIcodes()]))
idx = {}
for i, k in enumerate(keys):
    idx.setdefault(k, i)

coords = np.asarray(protein.getCoords(), float)
names = [str(n).strip() for n in protein.getNames()]
els = [str(e).strip().upper() for e in protein.getElements()]
pkeys = list(zip(protein.getChids(), protein.getResnums(),
                 [str(i) for i in protein.getIcodes()]))
for mode in ("any_atom", "sidechain"):
    brute = np.zeros(len(keys), bool)
    for i, k in enumerate(pkeys):
        if els[i] in ("H", "D"):
            continue
        if mode == "sidechain" and names[i] in BACKBONE:
            continue
        j = idx.get(k)
        if j is None:
            continue
        if np.sqrt(((oth - coords[i]) ** 2).sum(1)).min() <= CUTOFF:
            brute[j] = True
    key = "%s|all" % mode
    assert (brute == masks[key]).all(), \
        "%s: KD-tree and brute force disagree on %d residues" % (mode, (brute != masks[key]).sum())
    print("brute-force %-10s agrees on all %d residues (%d near)"
          % (mode, len(brute), int(brute.sum())))

print("ALL MASK CHECKS PASSED")
