"""Inputs whose context is only the class that names the split.

Why this exists. With the whole deposited file as input, ProteinMPNN reproduces
the paper on both the small-molecule and nucleotide splits while LigandMPNN comes
out high on both. ProteinMPNN never sees context atoms and LigandMPNN does, so
the obvious suspect is that our files hand LigandMPNN more context than the
authors gave it. The metal split says the same thing from the other side: the
authors' own scored-residue counts only make sense if the context was the metal
alone, not the sugars, sulfates and glycerol that are also in those files.

So: protein plus the nucleic acid for the nucleotide split, protein plus the
transition-metal atoms for the metal split, nothing else. This mirrors the
small-molecule split, where the authors' file names say outright that the input
was one chain plus one named ligand.

Extra analysis. The claim-sheet reading (whole deposited file) stays the primary.
"""

import json
import os
import sys

from prody import confProDy, parsePDB, writePDB

confProDy(verbosity="critical")

ROOT = "/mnt/e/Ciencia/pipeline/2025-dauparas-ligandmpnn"
VROOT = ROOT + "/verify"
TRANSITION = ("SC TI V CR MN FE CO NI CU ZN Y ZR NB MO TC RU RH PD AG CD "
              "HF TA W RE OS IR PT AU HG").split()

SPLITS = {
    "nucleotide": "protein or nucleic",
    "metal": "protein or (not protein and not water and element " + " ".join(TRANSITION) + ")",
}


def main():
    index = json.load(open(VROOT + "/inputs/index.json"))
    out_index = {}
    for split, selection in SPLITS.items():
        dest = "%s/inputs/%s_classonly" % (VROOT, split)
        os.makedirs(dest, exist_ok=True)
        made = []
        for entry in index[split]:
            atoms = parsePDB(entry["path"])
            sel = atoms.select(selection)
            if sel is None:
                print("EMPTY selection", split, entry["name"])
                continue
            path = os.path.join(dest, entry["name"] + ".pdb")
            writePDB(path, sel)
            made.append({"name": entry["name"], "pdb_id": entry["pdb_id"],
                         "path": path, "n_atoms": int(sel.numAtoms())})
        print(split, len(made), "of", len(index[split]))
        out_index[split + "_classonly"] = made
        with open("%s/inputs/%s_classonly_paths.json" % (VROOT, split), "w") as fh:
            json.dump({e["path"]: "" for e in made}, fh, indent=1)

    index.update(out_index)
    with open(VROOT + "/inputs/index.json", "w") as fh:
        json.dump(index, fh, indent=1)
    print("index.json updated")


if __name__ == "__main__":
    sys.exit(main())
