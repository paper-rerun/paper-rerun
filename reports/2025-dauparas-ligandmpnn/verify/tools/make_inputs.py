"""Build the model inputs for the three splits, one reading fixed before the run.

Small molecule: the authors' own Fig. 2b file names say what went in -
<id>_<chain><ligand>.pdb, e.g. 1a28_ASTR.pdb. So the input is that one protein
chain plus the copies of that one named ligand sitting in it, and nothing else:
no water, no other hetero groups, no other chains. Checked beforehand that all
317 named ligands really do appear in the named chain.

Nucleotide and metal: the names are bare <id>.pdb, which is what RCSB calls the
asymmetric unit (the biological assembly is <id>.pdb1). So those two splits use
the deposited file whole, untouched, straight from data/structures/asym.

MODEL/ENDMDL lines are carried over, because ProDy reads only the first model and
dropping them would merge every NMR model into one structure.
"""

import json
import os
import sys

ROOT = "/mnt/e/Ciencia/pipeline/2025-dauparas-ligandmpnn"
ASYM = ROOT + "/data/structures/asym"
VROOT = ROOT + "/verify"
OUT = VROOT + "/inputs"

KEEP_PREFIX = ("ATOM  ", "HETATM", "TER   ", "TER\n", "MODEL ", "ENDMDL")
WATER = ("HOH", "DOD", "WAT")


def build_small_molecule():
    names = json.load(open(ROOT + "/sources/fig2b_names.json"))["small_molecule"]
    dest = OUT + "/small_molecule"
    os.makedirs(dest, exist_ok=True)
    made = []
    for name in names:
        stem = name[:-4]
        pdb_id, chain, lig = stem[:4], stem[5], stem[6:]
        src = os.path.join(ASYM, pdb_id + ".pdb")
        kept_atom = kept_lig = 0
        out_lines = []
        with open(src, "r", errors="replace") as fh:
            for line in fh:
                rec = line[:6]
                if rec in ("MODEL ", "ENDMDL"):
                    out_lines.append(line)
                    continue
                if rec == "ATOM  " and line[21] == chain:
                    out_lines.append(line)
                    kept_atom += 1
                elif rec == "HETATM" and line[21] == chain:
                    resn = line[17:20].strip()
                    if resn in WATER:
                        continue
                    if resn == lig:
                        out_lines.append(line)
                        kept_lig += 1
                elif rec == "TER   " and line[21:22] == chain:
                    out_lines.append(line)
        out_lines.append("END\n")
        path = os.path.join(dest, stem + ".pdb")
        with open(path, "w") as fh:
            fh.writelines(out_lines)
        made.append(
            {"name": stem, "pdb_id": pdb_id, "chain": chain, "ligand": lig,
             "path": path, "n_atom_records": kept_atom, "n_ligand_atoms": kept_lig}
        )
        if kept_atom == 0 or kept_lig == 0:
            print("EMPTY", stem, kept_atom, kept_lig)
    return made


def whole_file(split, listname):
    ids = json.load(open(ROOT + "/repo/training/" + listname))
    # 5l70 only exists as mmCIF and its ligand id A1IJ4 is 5 characters, which does
    # not fit PDB's 3-column resName field; tools/fix_5l70.py writes a readable copy
    patched = VROOT + "/inputs/fixed/asym"
    made = []
    for pdb_id in ids:
        path = os.path.join(ASYM, pdb_id + ".pdb")
        alt = os.path.join(patched, pdb_id + ".pdb")
        if os.path.exists(alt):
            path = alt
        made.append({"name": pdb_id, "pdb_id": pdb_id, "chain": None,
                     "ligand": None, "path": path,
                     "bytes": os.path.getsize(path)})
    return made


def main():
    os.makedirs(OUT, exist_ok=True)
    index = {
        "assembly_choice": "asymmetric unit (RCSB <id>.pdb) for all three splits",
        "small_molecule": build_small_molecule(),
        "nucleotide": whole_file("nucleotide", "test_nucleotide.json"),
        "metal": whole_file("metal", "test_metal.json"),
    }
    for split in ("small_molecule", "nucleotide", "metal"):
        print(split, len(index[split]))
    with open(OUT + "/index.json", "w") as fh:
        json.dump(index, fh, indent=1)

    # the json run.py wants for --pdb_path_multi: only the keys are read
    for split in ("small_molecule", "nucleotide", "metal"):
        with open(OUT + "/%s_paths.json" % split, "w") as fh:
            json.dump({e["path"]: "" for e in index[split]}, fh, indent=1)

    names = [e["name"] for e in index["small_molecule"]]
    assert len(set(names)) == len(names), "duplicate small-molecule name"


if __name__ == "__main__":
    sys.exit(main())
