"""5l70 (metal split) has no PDB-format file at RCSB, only mmCIF.

run.py parses with ProDy's parsePDB, which does not read mmCIF, so the entry is
unusable as downloaded. Fetch the mmCIF and try to write it back out as PDB with
ProDy itself. If that fails the entry stays on the shelf and the run stage drops
it from the metal split, with the drop recorded (83 -> 82).
"""

import gzip
import json
import os
import urllib.request

ROOT = "/mnt/e/Ciencia/pipeline/2025-dauparas-ligandmpnn"
OUT = ROOT + "/data/structures"
PDB_ID = "5l70"

os.makedirs(OUT + "/mmcif", exist_ok=True)
cif = OUT + "/mmcif/%s.cif" % PDB_ID

if not os.path.exists(cif):
    url = "https://files.rcsb.org/download/%s.cif.gz" % PDB_ID
    req = urllib.request.Request(url, headers={"User-Agent": "repro-pipeline/1.0"})
    with urllib.request.urlopen(req, timeout=120) as resp:
        raw = gzip.decompress(resp.read())
    with open(cif, "wb") as fh:
        fh.write(raw)
print("mmcif bytes:", os.path.getsize(cif))

asm = OUT + "/mmcif/%s-assembly1.cif" % PDB_ID
if not os.path.exists(asm):
    url = "https://files.rcsb.org/download/%s-assembly1.cif.gz" % PDB_ID
    req = urllib.request.Request(url, headers={"User-Agent": "repro-pipeline/1.0"})
    with urllib.request.urlopen(req, timeout=120) as resp:
        raw = gzip.decompress(resp.read())
    with open(asm, "wb") as fh:
        fh.write(raw)
print("assembly1 mmcif bytes:", os.path.getsize(asm))

note = {"pdb_id": PDB_ID, "split": "metal", "mmcif": cif, "mmcif_assembly1": asm}

from prody import parseMMCIF, writePDB

for src, flavour in ((cif, "asym"), (asm, "biounit1")):
    key = "convert_" + flavour
    try:
        atoms = parseMMCIF(src)
        dest = OUT + "/%s/%s.pdb" % (flavour, PDB_ID)
        writePDB(dest, atoms)
        note[key] = {
            "status": "converted",
            "n_atoms": int(atoms.numAtoms()),
            "n_chains": len(set(atoms.getChids())),
            "path": dest,
            "bytes": os.path.getsize(dest),
        }
    except Exception as err:
        note[key] = {"status": "failed", "error": "%s: %s" % (type(err).__name__, err)}

with open(OUT + "/5l70_note.json", "w") as fh:
    json.dump(note, fh, indent=1)
print(json.dumps(note, indent=1))
