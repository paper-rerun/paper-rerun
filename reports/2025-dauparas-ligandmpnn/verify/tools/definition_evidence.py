"""How well does each fixed reading reproduce the authors' own scored-residue counts?

For every protein the authors published three recovery values (Rosetta,
ProteinMPNN, LigandMPNN), each a mean over 10 sequences of count/n. That pins n.
This compares the pinned n against the reading this verification fixed for each
split, and reports the exact-match rate - the evidence behind the choice.
"""

import collections
import csv
import json
import os
import sys

sys.path.insert(0, "/mnt/e/Ciencia/pipeline/2025-dauparas-ligandmpnn/verify/tools")

import numpy as np

from score_recovery import masks_for

ROOT = "/mnt/e/Ciencia/pipeline/2025-dauparas-ligandmpnn"
SD = ROOT + "/sources/sd/x/s2"
METHODS = ["Rosetta", "ProteinMPNN", "LigandMPNN"]
STEM = {"small_molecule": "fig_2_1", "nucleotide": "fig_2_2", "metal": "fig_2_3"}
PRIMARY = {"small_molecule": "any_atom|all",
           "nucleotide": "any_atom|all",
           "metal": "any_atom|metal_transition"}


def fits(value, n):
    t = value * n / 10.0
    return abs(t - round(t)) < max(1e-3, abs(t) * 1e-6)


def smallest_n(values, n_max=1500):
    for n in range(1, n_max + 1):
        if all(fits(v, n) for v in values):
            return n
    return None


def main():
    report = {}
    for split in ("small_molecule", "nucleotide", "metal"):
        rows = list(csv.DictReader(open(os.path.join(SD, STEM[split] + "_1.csv"))))
        vals = {m: np.array([float(r["probs"]) for r in rows if r["types"] == m])
                for m in METHODS}
        index = json.load(open(ROOT + "/verify/inputs/index.json"))[split]

        tally = collections.Counter()
        detail = []
        for i, entry in enumerate(index):
            n_true = smallest_n([vals[m][i] for m in METHODS])
            try:
                masks, _ = masks_for(entry["path"])
            except Exception as err:
                detail.append({"name": entry["name"], "n_true": n_true,
                               "error": type(err).__name__})
                continue
            row = {"name": entry["name"], "n_true": n_true}
            for key, mask in masks.items():
                row[key] = int(mask.sum())
                if n_true is not None and int(mask.sum()) == n_true:
                    tally[key] += 1
            detail.append(row)
            if (i + 1) % 50 == 0:
                print("  ...", split, i + 1, "/", len(index), flush=True)

        n = sum(1 for r in detail if r.get("n_true") is not None and "error" not in r)
        print("\n=== %s (%d proteins) ===" % (split, n))
        print("    primary reading here: %s" % PRIMARY[split])
        for k, v in tally.most_common():
            star = "  <= primary" if k == PRIMARY[split] else ""
            print("    %-28s exact n match %3d / %3d  (%.0f%%)%s"
                  % (k, v, n, 100.0 * v / n, star))
        report[split] = {"n": n, "tally": dict(tally), "primary": PRIMARY[split],
                         "detail": detail}

    with open(ROOT + "/verify/out/definition_evidence.json", "w") as fh:
        json.dump(report, fh, indent=1, default=float)
    print("\nwrote verify/out/definition_evidence.json")


if __name__ == "__main__":
    sys.exit(main())
