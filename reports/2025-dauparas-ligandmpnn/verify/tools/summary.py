"""Everything in one table: each claim under the fixed reading, then the variants.

The per-protein bias column is the sharpest number here. A median can land on the
paper's value by luck; the mean difference across 317, 74 or 83 proteins, each one
compared against the authors' own published value for that protein, cannot.
"""

import csv
import json
import os

import numpy as np

ROOT = "/mnt/e/Ciencia/pipeline/2025-dauparas-ligandmpnn"
VROOT = ROOT + "/verify"
SD = ROOT + "/sources/sd/x/s2"
STEM = {"small_molecule": "fig_2_1", "nucleotide": "fig_2_2", "metal": "fig_2_3"}
PAPER = {  # split -> method -> (median, mean) as published in Source Data Fig. 2
    "small_molecule": {"LigandMPNN": (63.333, 61.384), "ProteinMPNN": (50.476, 50.730)},
    "nucleotide": {"LigandMPNN": (50.516, 49.793), "ProteinMPNN": (34.031, 34.201)},
    "metal": {"LigandMPNN": (77.500, 75.556), "ProteinMPNN": (40.566, 41.895)},
}
TOL = {"small_molecule": 1.0, "nucleotide": 2.0, "metal": 2.0}
HEADLINE = {"small_molecule": {"LigandMPNN": 63.3, "ProteinMPNN": 50.5},
            "nucleotide": {"LigandMPNN": 50.5, "ProteinMPNN": 34.0},
            "metal": {"LigandMPNN": 77.5, "ProteinMPNN": 40.6}}

# (claim, label, split-for-paper, score file stem, scoring key)
ROWS = [
    ("C1", "LigandMPNN 0.1A, chain+ligand        [claim-sheet reading]",
     "small_molecule", "ligand_mpnn_small_molecule", "any_atom|all"),
    ("C1*", "LigandMPNN 0.2A, chain+ligand",
     "small_molecule", "ligand_mpnn_small_molecule_from_small_molecule_noise020", "any_atom|all"),
    ("C1s", "LigandMPNN 0.1A, sidechain scoring",
     "small_molecule", "ligand_mpnn_small_molecule", "sidechain|all"),
    ("C2", "ProteinMPNN 0.1A, chain+ligand       [claim-sheet reading]",
     "small_molecule", "protein_mpnn_small_molecule", "any_atom|all"),
    ("C2*", "ProteinMPNN 0.2A, chain+ligand",
     "small_molecule", "protein_mpnn_small_molecule_from_small_molecule_noise020", "any_atom|all"),
    ("C3", "LigandMPNN 0.1A, whole asym unit     [claim-sheet reading]",
     "nucleotide", "ligand_mpnn_nucleotide", "any_atom|all"),
    ("C3a", "LigandMPNN 0.2A, whole asym unit",
     "nucleotide", "ligand_mpnn_nucleotide_from_nucleotide_noise020", "any_atom|all"),
    ("C3b", "LigandMPNN 0.1A, protein+nucleic only",
     "nucleotide", "ligand_mpnn_nucleotide_classonly", "any_atom|all"),
    ("C3*", "LigandMPNN 0.2A, protein+nucleic only",
     "nucleotide", "ligand_mpnn_nucleotide_classonly_from_nucleotide_classonly_noise020", "any_atom|all"),
    ("C4", "ProteinMPNN 0.1A, whole asym unit    [claim-sheet reading]",
     "nucleotide", "protein_mpnn_nucleotide", "any_atom|all"),
    ("C5", "LigandMPNN 0.1A, whole file, metal-only scoring",
     "metal", "ligand_mpnn_metal", "any_atom|metal_transition"),
    ("C5a", "LigandMPNN 0.2A, whole file, metal-only scoring",
     "metal", "ligand_mpnn_metal_from_metal_noise020", "any_atom|metal_transition"),
    ("C5b", "LigandMPNN 0.1A, protein+metal only",
     "metal", "ligand_mpnn_metal_classonly", "any_atom|all"),
    ("C5*", "LigandMPNN 0.2A, protein+metal only",
     "metal", "ligand_mpnn_metal_classonly_from_metal_classonly_noise020", "any_atom|all"),
    ("C5c", "LigandMPNN 0.1A, all-hetero scoring  [claim-sheet reading]",
     "metal", "ligand_mpnn_metal", "any_atom|all"),
    ("C6", "ProteinMPNN 0.1A, metal-only scoring",
     "metal", "protein_mpnn_metal", "any_atom|metal_transition"),
    ("C6b", "ProteinMPNN 0.1A, all-hetero scoring [claim-sheet reading]",
     "metal", "protein_mpnn_metal", "any_atom|all"),
]


def authors(split, method):
    path = os.path.join(SD, STEM[split] + "_1.csv")
    return np.array([float(r["probs"]) for r in csv.DictReader(open(path))
                     if r["types"] == method])


def main():
    print("%-5s %-52s %-8s %-8s %-7s %-8s %-6s %s" %
          ("id", "configuration", "ourMed", "paperMed", "diff", "bias/prot", "r", "verdict"))
    print("-" * 124)
    out = []
    for cid, label, split, stem, key in ROWS:
        path = "%s/out/score_%s.json" % (VROOT, stem)
        if not os.path.exists(path):
            print("%-5s %-52s MISSING" % (cid, label))
            continue
        d = json.load(open(path))
        method = "LigandMPNN" if "ligand_mpnn" in stem else "ProteinMPNN"
        mine = np.array([r[key]["recovery"] if key in r and r[key]["recovery"] is not None
                         else np.nan for r in d["per_protein"]])
        ok = ~np.isnan(mine)
        med = float(np.median(mine[ok]))
        pmed, pmean = PAPER[split][method]
        th = authors(split, method)
        bias = float((mine[ok] - th[ok]).mean())
        r = float(np.corrcoef(mine[ok], th[ok])[0, 1])
        head = HEADLINE[split][method]
        diff = med - head
        verdict = "match" if abs(diff) <= TOL[split] else "MISS"
        print("%-5s %-52s %-8.3f %-8.1f %-+7.2f %-+8.2f %-6.3f %s%s" %
              (cid, label, med, head, diff, bias, r, verdict,
               "" if ok.sum() == len(mine) else "  (n=%d of %d)" % (ok.sum(), len(mine))))
        out.append({"id": cid, "label": label, "split": split, "method": method,
                    "scoring_key": key, "our_median": med, "our_mean": float(mine[ok].mean()),
                    "paper_headline": head, "paper_sd_median": pmed, "paper_sd_mean": pmean,
                    "diff": diff, "tolerance": TOL[split],
                    "per_protein_bias": bias, "pearson_r": r,
                    "n": int(ok.sum()), "n_total": int(len(mine))})
    with open(VROOT + "/out/summary.json", "w") as fh:
        json.dump(out, fh, indent=1)
    print("\nwrote verify/out/summary.json")


if __name__ == "__main__":
    main()
