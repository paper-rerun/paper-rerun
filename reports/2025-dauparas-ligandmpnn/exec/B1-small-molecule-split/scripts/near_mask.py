"""Per-structure near-ligand masks, in parse_PDB residue order.

Two masks per structure:
  near      - the fixed definition: a residue counts if any SIDE-CHAIN atom
              (every deposited atom other than N, CA, C, O, OXT; hydrogens
              ignored) is within 5.0 A of a non-protein, non-water heavy atom.
  near_any  - the same with every heavy atom of the residue, backbone included.
              This is the Fig. 2a legend wording and it is the one that
              reproduces the authors' own denominators (see test_definitions.py).

The parsing mirrors data_utils.parse_PDB so the masks line up index for index
with run.py's native/generated sequences: parsePDB, drop occupancy == 0, select
"protein", order by the CA atoms.
"""

import json
import os

import numpy as np
from prody import parsePDB, confProDy

confProDy(verbosity="none")

ROOT = "/mnt/e/Ciencia/pipeline/2025-dauparas-ligandmpnn"
BASE = os.path.join(ROOT, "exec/B1-small-molecule-split")
BACKBONE = {"N", "CA", "C", "O", "OXT"}
CUTOFF = 5.0

restype_3to1 = {
    "ALA": "A", "ARG": "R", "ASN": "N", "ASP": "D", "CYS": "C", "GLN": "Q",
    "GLU": "E", "GLY": "G", "HIS": "H", "ILE": "I", "LEU": "L", "LYS": "K",
    "MET": "M", "PHE": "F", "PRO": "P", "SER": "S", "THR": "T", "TRP": "W",
    "TYR": "Y", "VAL": "V",
}


def mask_for(path):
    atoms = parsePDB(path).select("occupancy > 0")
    protein = atoms.select("protein")
    other = atoms.select("not protein and not water")

    ca = protein.select("name CA")
    order = [(c, int(r), i) for c, r, i in
             zip(ca.getChids(), ca.getResnums(), ca.getIcodes())]
    native = "".join(restype_3to1.get(n, "X") for n in ca.getResnames())
    pos = {k: n for n, k in enumerate(order)}

    near = np.zeros(len(order), dtype=bool)
    near_any = np.zeros(len(order), dtype=bool)
    if other is None:
        return near, near_any, native, order, 0

    y = other.getCoords()[
        np.array([e.strip().upper() != "H" for e in other.getElements()])]
    if len(y) == 0:
        return near, near_any, native, order, 0

    names = protein.getNames()
    heavy = np.array([e.strip().upper() != "H" for e in protein.getElements()])
    side = np.array([n not in BACKBONE for n in names]) & heavy

    xyz = protein.getCoords()
    key = list(zip(protein.getChids(), [int(v) for v in protein.getResnums()],
                   protein.getIcodes()))

    hit = np.zeros(len(xyz), dtype=bool)
    step = 4096
    for s in range(0, len(xyz), step):
        d2 = ((xyz[s:s + step, None, :] - y[None, :, :]) ** 2).sum(-1)
        hit[s:s + step] = d2.min(1) <= CUTOFF ** 2

    for i, (h, k) in enumerate(zip(hit, key)):
        if not h or k not in pos:
            continue
        if heavy[i]:
            near_any[pos[k]] = True
        if side[i]:
            near[pos[k]] = True
    return near, near_any, native, order, len(y)


if __name__ == "__main__":
    man = json.load(open(os.path.join(BASE, "inputs_manifest.json")))
    out = {}
    for rec in man["records"]:
        near, near_any, native, order, n_ctx = mask_for(rec["input"])
        out[rec["name"][:-4]] = {
            "n_res": len(order),
            "n_near": int(near.sum()),
            "n_near_any_atom": int(near_any.sum()),
            "n_context_heavy_atoms": int(n_ctx),
            "native": native,
            "near": "".join("1" if b else "0" for b in near),
            "near_any_atom": "".join("1" if b else "0" for b in near_any),
        }
    json.dump(out, open(os.path.join(BASE, "near_mask.json"), "w"))
    ns = [v["n_near"] for v in out.values()]
    na = [v["n_near_any_atom"] for v in out.values()]
    print("structures", len(out))
    print("side-chain atoms  : min %d median %d max %d" % (min(ns), np.median(ns), max(ns)))
    print("any heavy atom    : min %d median %d max %d" % (min(na), np.median(na), max(na)))
