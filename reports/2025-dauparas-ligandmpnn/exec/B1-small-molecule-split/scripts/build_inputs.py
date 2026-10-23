"""Build the 317 small-molecule inputs: one protein chain + one named ligand.

Reading fixed before running (see manifest "reading" field):
  - source file = asymmetric unit (data/structures/asym/<id>.pdb), because the
    chain letter in the authors' Source Data names is an auth chain id of the
    deposited entry.
  - keep the protein atoms of that chain plus ONE copy of the named ligand,
    the copy closest to that chain. Every other hetero atom and all waters are
    dropped, so "all non-protein atoms" reduces to that ligand.
"""

import json
import os
import sys

import numpy as np
from prody import parsePDB, writePDB, confProDy

confProDy(verbosity="none")

ROOT = "/mnt/e/Ciencia/pipeline/2025-dauparas-ligandmpnn"
ASYM = os.path.join(ROOT, "data/structures/asym")
OUT = os.path.join(ROOT, "exec/B1-small-molecule-split/inputs")
MANIFEST = os.path.join(ROOT, "exec/B1-small-molecule-split/inputs_manifest.json")

names = json.load(open(os.path.join(ROOT, "sources/fig2b_names.json")))["small_molecule"]

records = []
failures = []

for name in names:
    stem = name[:-4]              # 1a28_ASTR
    pdbid = stem[:4]
    chain = stem[5]
    lig = stem[6:]

    path = os.path.join(ASYM, pdbid + ".pdb")
    atoms = parsePDB(path)
    if atoms is None:
        failures.append({"name": name, "why": "parse failed"})
        continue

    resnames = atoms.getResnames()
    chids = atoms.getChids()
    resnums = atoms.getResnums()
    icodes = atoms.getIcodes()
    hetero = atoms.getFlags("hetatm")

    prot_flag = atoms.getFlags("protein")
    prot_idx = np.where(prot_flag & (chids == chain))[0]
    if len(prot_idx) == 0:
        failures.append({"name": name, "why": "no protein atoms in chain " + chain})
        continue
    prot_xyz = atoms.getCoords()[prot_idx]

    # Candidate ligand copies: hetero atoms with the named residue name
    lig_flag = hetero & (resnames == lig)
    cand = np.where(lig_flag)[0]
    if len(cand) == 0:
        failures.append({"name": name, "why": "ligand %s not found" % lig})
        continue

    # Group candidates into residue copies and take the one closest to the chain
    keys = {}
    for i in cand:
        keys.setdefault((chids[i], int(resnums[i]), icodes[i]), []).append(i)

    best_key, best_idx, best_d = None, None, 1e9
    for k, idx in keys.items():
        xyz = atoms.getCoords()[idx]
        d = np.sqrt(((prot_xyz[:, None, :] - xyz[None, :, :]) ** 2).sum(-1)).min()
        if d < best_d:
            best_key, best_idx, best_d = k, idx, float(d)

    keep = np.concatenate([prot_idx, np.array(best_idx)])
    keep.sort()
    out_path = os.path.join(OUT, stem + ".pdb")
    writePDB(out_path, atoms[keep])

    records.append({
        "name": name,
        "pdb_id": pdbid,
        "chain": chain,
        "ligand": lig,
        "ligand_copy": [best_key[0], best_key[1], best_key[2]],
        "ligand_copies_in_file": len(keys),
        "ligand_atoms_kept": len(best_idx),
        "min_dist_chain_ligand": round(best_d, 3),
        "protein_atoms": int(len(prot_idx)),
        "input": out_path,
    })

json.dump({
    "reading": "asymmetric unit; one protein chain + the nearest copy of the named ligand; waters and all other hetero atoms dropped",
    "n_built": len(records),
    "n_failed": len(failures),
    "failures": failures,
    "records": records,
}, open(MANIFEST, "w"), indent=1)

print("built", len(records), "failed", len(failures))
for f in failures:
    print("FAIL", f)
