"""Do the metal ions actually reach the model?

The claim sheet warns that parse_PDB maps an element through
    element_dict[y_t.upper()] if y_t.upper() in element_list else 0
and that if element_list were title-case ('Zn', 'Fe', ...) then every two-letter
symbol would fall to 0 and be dropped, which would gut the metal split. So this
measures it instead of assuming: run the installed parser on a few metal entries
and count what survives, element by element.
"""

import collections
import json
import os
import sys

sys.path.insert(0, "/mnt/e/Ciencia/pipeline/2025-dauparas-ligandmpnn/verify/repo")

import numpy as np
from prody import confProDy, parsePDB

import data_utils

confProDy(verbosity="critical")

ROOT = "/mnt/e/Ciencia/pipeline/2025-dauparas-ligandmpnn"
ASYM = ROOT + "/data/structures/asym"

# what the installed code's own list looks like after its uppercase pass
print("element_list is uppercased inside parse_PDB:",
      "ZN" in [e.upper() for e in data_utils.element_list])

ids = json.load(open(ROOT + "/repo/training/test_metal.json"))[:6]
report = {}

for pdb_id in ids:
    path = os.path.join(ASYM, pdb_id + ".pdb")
    out, backbone, other_atoms, icodes, water = data_utils.parse_PDB(path, device="cpu")

    raw = collections.Counter()
    if other_atoms is not None:
        raw = collections.Counter(str(e).strip().upper() for e in other_atoms.getElements())

    y_t = out["Y_t"].numpy()
    y_m = out["Y_m"].numpy()
    kept = collections.Counter()
    rev = {v: k for k, v in
           zip([e.upper() for e in data_utils.element_list],
               range(1, len(data_utils.element_list)))}
    for t in y_t:
        kept[rev.get(int(t), "?%d" % t)] += 1

    metals = {"ZN", "FE", "MG", "CA", "MN", "CU", "NA", "K", "CL", "NI", "CO", "CD", "HG", "MO", "W"}
    report[pdb_id] = {
        "n_other_atoms_in_file": int(sum(raw.values())),
        "n_context_atoms_reaching_model": int(len(y_t)),
        "raw_elements": dict(raw.most_common(12)),
        "kept_elements": dict(kept.most_common(12)),
        "metal_atoms_in_file": {k: v for k, v in raw.items() if k in metals},
        "metal_atoms_kept": {k: v for k, v in kept.items() if k in metals},
    }
    print(pdb_id, json.dumps(report[pdb_id], indent=1))

dest = ROOT + "/verify/out/context_atom_check.json"
os.makedirs(os.path.dirname(dest), exist_ok=True)
with open(dest, "w") as fh:
    json.dump(report, fh, indent=1)
print("wrote", dest)
