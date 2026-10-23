"""Make 5l70 readable by prody's parsePDB.

5l70 holds the ligand A1IJ4, one of the new 5-character CCD codes. The legacy PDB
columns give the residue name 3, so the converted file carries the name over
columns 18-22 and pushes chain, resSeq and the coordinates two columns right:

  HETATM 4022  O   A1IJ4 C 302      57.991  12.286  46.317  1.00 27.09   C O

prody then reads '91  12.2' as the y coordinate and raises PDBParseError. The fix
renames that one ligand to LIG and shifts the rest of the line back by two, which
leaves every coordinate, element and atom name untouched. Nothing else in the 83
metal entries has an over-long residue name (scanned).

Writes fixed copies under exec/B3-metal-split/fixed/<flavor>/5l70.pdb; the
downloaded structures are left alone.
"""

import os
import shutil

ROOT = "/mnt/e/Ciencia/pipeline/2025-dauparas-ligandmpnn"
EXEC = ROOT + "/exec/B3-metal-split"
LONG_NAME = "A1IJ4"
NEW_NAME = "LIG"

for flavor in ("biounit1", "asym"):
    src = "%s/data/structures/%s/5l70.pdb" % (ROOT, flavor)
    dst_dir = "%s/fixed/%s" % (EXEC, flavor)
    os.makedirs(dst_dir, exist_ok=True)
    dst = dst_dir + "/5l70.pdb"

    seen = set()
    n_fixed = 0
    with open(src) as fh, open(dst, "w") as out:
        for line in fh:
            if line.startswith(("ATOM", "HETATM")):
                seen.add(line[17:20].strip())
                if line[17:22] == LONG_NAME:
                    line = line[:17] + NEW_NAME + line[22:]
                    n_fixed += 1
            out.write(line)

    assert NEW_NAME not in seen, "LIG already used in %s" % src
    # Every record must now parse as a PDB coordinate line
    with open(dst) as fh:
        for i, line in enumerate(fh, 1):
            if line.startswith(("ATOM", "HETATM")):
                for a, b in ((30, 38), (38, 46), (46, 54)):
                    float(line[a:b])
    print("%s: renamed %d %s lines -> %s, wrote %s"
          % (flavor, n_fixed, LONG_NAME, NEW_NAME, dst))
