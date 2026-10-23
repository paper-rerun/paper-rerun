"""5l70 is the one metal entry RCSB has no PDB file for, only mmCIF.

The conversion in tools/07_get_5l70.py reports success, but the file it writes
cannot be read back: 5l70 carries a ligand whose chemical component id is A1IJ4,
five characters, and PDB format gives resName three columns. ProDy writes it
anyway, the name spills into the chain and residue-number columns, and parsing
dies at line 4023 with "invalid or missing coordinate(s)".

Fix: shorten every component id longer than three characters before writing. Only
the label changes - coordinates, elements, chains and residue numbers are
untouched - and the model reads context atoms by element, never by residue name,
so nothing the model sees is altered. The mapping is written out beside the file.

This is a file-format repair, not a change to the authors' method.
"""

import json
import os
import sys

from prody import confProDy, parseMMCIF, parsePDB, writePDB

confProDy(verbosity="critical")

ROOT = "/mnt/e/Ciencia/pipeline/2025-dauparas-ligandmpnn"
OUT = ROOT + "/verify/inputs/fixed"
os.makedirs(OUT, exist_ok=True)

note = {"pdb_id": "5l70", "reason": "component id longer than 3 characters"}

for src, flavour in ((ROOT + "/data/structures/mmcif/5l70.cif", "asym"),
                     (ROOT + "/data/structures/mmcif/5l70-assembly1.cif", "biounit1")):
    atoms = parseMMCIF(src)
    resnames = atoms.getResnames()
    mapping = {}
    new = []
    for r in resnames:
        r = str(r)
        if len(r) > 3:
            if r not in mapping:
                mapping[r] = "L%02d" % (len(mapping) + 1)
            new.append(mapping[r])
        else:
            new.append(r)
    atoms.setResnames(new)

    dest = "%s/5l70_%s.pdb" % (OUT, flavour)
    writePDB(dest, atoms)

    back = parsePDB(dest)          # must survive the round trip now
    note[flavour] = {
        "path": dest,
        "renamed": mapping,
        "n_atoms_written": int(atoms.numAtoms()),
        "n_atoms_read_back": int(back.numAtoms()),
        "n_protein_ca": int(len(back.select("protein").select("name CA"))),
    }
    print(flavour, json.dumps(note[flavour], indent=1))

with open(OUT + "/5l70_fix.json", "w") as fh:
    json.dump(note, fh, indent=1)
print("wrote", OUT + "/5l70_fix.json")
