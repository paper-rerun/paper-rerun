"""What the installed parse_PDB actually keeps as context atoms.

The definition warns that element_dict could drop every two-letter element
symbol. In this commit data_utils.py line 648 uppercases element_list before
building element_dict, so y_t.upper() does match two-letter symbols. Check it
against the deposited atoms instead of trusting the read.
"""
import json
import os
import sys
from collections import Counter

import numpy as np
from prody import parsePDB, confProDy

sys.path.insert(0, "/mnt/e/Ciencia/pipeline/2025-dauparas-ligandmpnn/repo")
from data_utils import parse_PDB

confProDy(verbosity="none")
BASE = "/mnt/e/Ciencia/pipeline/2025-dauparas-ligandmpnn/exec/B1-small-molecule-split"

man = json.load(open(os.path.join(BASE, "inputs_manifest.json")))["records"]

report = {"per_structure": [], "elements_seen": {}, "elements_dropped": {}}
seen, dropped = Counter(), Counter()
mismatch = 0

for rec in man:
    path = rec["input"]
    pd, _, other, _, _ = parse_PDB(path, device="cpu", chains=[],
                                   parse_all_atoms=False,
                                   parse_atoms_with_zero_occupancy=False)
    kept = int(pd["Y_m"].sum())
    els = [e.strip().upper() for e in other.getElements()] if other is not None else []
    heavy = [e for e in els if e != "H"]
    seen.update(heavy)
    if kept != len(heavy):
        mismatch += 1
        # which elements went missing
        dropped.update(heavy)
    report["per_structure"].append({
        "name": rec["name"], "ligand": rec["ligand"],
        "deposited_heavy": len(heavy), "kept_by_parse_PDB": kept,
    })

report["elements_seen"] = dict(seen)
report["n_structures"] = len(man)
report["n_with_mismatch"] = mismatch
json.dump(report, open(os.path.join(BASE, "context_atom_check.json"), "w"), indent=1)

print("structures:", len(man), " context-atom count mismatches:", mismatch)
print("elements in the ligands:", dict(sorted(seen.items(), key=lambda x: -x[1])))
two = {e: c for e, c in seen.items() if len(e) > 1}
print("two-letter element symbols present:", two)
