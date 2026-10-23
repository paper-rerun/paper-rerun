"""Put our recovery next to the paper's, claim by claim.

Also compares protein by protein against Source Data Fig. 2, which is a far
sharper check than the median alone: a median can land on the paper's value with
the wrong residues scored, 317 per-protein values cannot.

Each split is scored under the reading fixed for it (see definition_evidence.py),
and every other reading is printed beside it so the choice stays visible.
"""

import csv
import json
import os
import sys

import numpy as np

ROOT = "/mnt/e/Ciencia/pipeline/2025-dauparas-ligandmpnn"
VROOT = ROOT + "/verify"
SD = ROOT + "/sources/sd/x/s2"

CLAIMS = [
    ("C1-LMPNN-SMALLMOL", "ligand_mpnn", "small_molecule", 63.3, 1.0, "LigandMPNN"),
    ("C2-PMPNN-SMALLMOL", "protein_mpnn", "small_molecule", 50.5, 1.0, "ProteinMPNN"),
    ("C3-LMPNN-NUCLEOTIDE", "ligand_mpnn", "nucleotide", 50.5, 2.0, "LigandMPNN"),
    ("C4-PMPNN-NUCLEOTIDE", "protein_mpnn", "nucleotide", 34.0, 2.0, "ProteinMPNN"),
    ("C5-LMPNN-METAL", "ligand_mpnn", "metal", 77.5, 2.0, "LigandMPNN"),
    ("C6-PMPNN-METAL", "protein_mpnn", "metal", 40.6, 2.0, "ProteinMPNN"),
]
STEM = {"small_molecule": "fig_2_1", "nucleotide": "fig_2_2", "metal": "fig_2_3"}
PRIMARY = {"small_molecule": "any_atom|all",
           "nucleotide": "any_atom|all",
           "metal": "any_atom|metal_transition"}
ALL_KEYS = ["any_atom|all", "sidechain|all", "any_atom|metal_transition"]


def authors_values(split, method):
    path = os.path.join(SD, STEM[split] + "_1.csv")
    return np.array([float(r["probs"]) for r in csv.DictReader(open(path))
                     if r["types"] == method])


def main():
    results = []
    print("%-22s %-7s %-8s %-8s %-5s %s" %
          ("claim", "paper", "ours", "diff", "tol", "verdict"))
    print("-" * 72)
    for cid, model, split, paper, tol, method in CLAIMS:
        path = "%s/out/score_%s_%s.json" % (VROOT, model, split)
        if not os.path.exists(path):
            print("%-22s %-7.1f %s" % (cid, paper, "NOT RUN"))
            continue
        d = json.load(open(path))
        key = PRIMARY[split]
        ours = d[key]["median_recovery"]
        n = d[key]["n_proteins"]
        if ours is None:
            print("%-22s %-7.1f no value" % (cid, paper))
            continue
        diff = ours - paper
        verdict = "match" if abs(diff) <= tol else "MISS"
        print("%-22s %-7.1f %-8.3f %-+8.3f %-5.1f %s  (n=%d, mean=%.2f)" %
              (cid, paper, ours, diff, tol, verdict, n, d[key]["mean_recovery"]))

        others = "   other readings: " + "  ".join(
            "%s=%.2f" % (k.replace("any_atom", "any").replace("sidechain", "sc")
                         .replace("metal_transition", "metal"), d[k]["median_recovery"])
            for k in ALL_KEYS if k != key and d.get(k, {}).get("median_recovery") is not None)
        print(others)

        theirs = authors_values(split, method)
        mine = np.array([r[key]["recovery"] if key in r and r[key]["recovery"] is not None
                         else np.nan for r in d["per_protein"]])
        ok = ~np.isnan(mine)
        per = {}
        if ok.sum() > 1:
            delta = mine[ok] - theirs[ok]
            per = {"n_compared": int(ok.sum()),
                   "mean_abs_diff": float(np.abs(delta).mean()),
                   "median_abs_diff": float(np.median(np.abs(delta))),
                   "within_5pp": float((np.abs(delta) <= 5).mean() * 100),
                   "pearson_r": float(np.corrcoef(mine[ok], theirs[ok])[0, 1])}
            print("   vs Source Data per protein: mean|d|=%.2f pp  median|d|=%.2f pp  "
                  "r=%.3f  within 5 pp: %.0f%%" %
                  (per["mean_abs_diff"], per["median_abs_diff"],
                   per["pearson_r"], per["within_5pp"]))

        results.append({"claim_id": cid, "model": model, "split": split,
                        "scoring_key": key, "paper_value": paper,
                        "our_value": ours, "diff": diff, "tolerance": tol,
                        "verdict": verdict, "n": n,
                        "mean_ours": d[key]["mean_recovery"],
                        "medians_all_readings": {k: d[k]["median_recovery"]
                                                 for k in ALL_KEYS if k in d},
                        "per_protein_vs_source_data": per,
                        "n_errors": len(d.get("errors", []))})

    dest = VROOT + "/out/comparison.json"
    with open(dest, "w") as fh:
        json.dump({"results": results}, fh, indent=1)
    print("\nwrote", dest)


if __name__ == "__main__":
    sys.exit(main())
