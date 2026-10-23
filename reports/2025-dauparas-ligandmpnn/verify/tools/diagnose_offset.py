"""Where does the gap between our median and the paper's come from?

Splits the comparison two ways:
  - proteins whose scored-residue count we reproduce exactly vs the rest, which
    separates "wrong input" from "same input, different numbers";
  - our value minus theirs as a distribution, to see whether it is an offset on
    every protein or a few proteins pulling the median.
"""

import csv
import json
import os
import sys

import numpy as np

ROOT = "/mnt/e/Ciencia/pipeline/2025-dauparas-ligandmpnn"
SD = ROOT + "/sources/sd/x/s2"
STEM = {"small_molecule": "fig_2_1", "nucleotide": "fig_2_2", "metal": "fig_2_3"}


def main():
    split, model, method = sys.argv[1], sys.argv[2], sys.argv[3]
    key = sys.argv[4] if len(sys.argv) > 4 else "any_atom|all"

    score = json.load(open("%s/verify/out/score_%s_%s.json" % (ROOT, model, split)))
    ev = json.load(open(ROOT + "/verify/out/definition_evidence.json"))[split]
    n_true = {r["name"]: r.get("n_true") for r in ev["detail"]}
    n_mine_ev = {r["name"]: r.get(ev["primary"]) for r in ev["detail"]}

    rows = list(csv.DictReader(open(os.path.join(SD, STEM[split] + "_1.csv"))))
    theirs = np.array([float(r["probs"]) for r in rows if r["types"] == method])

    mine, match, names, ns = [], [], [], []
    for i, r in enumerate(score["per_protein"]):
        v = r.get(key, {}).get("recovery") if key in r else None
        mine.append(np.nan if v is None else v)
        names.append(r["name"])
        ns.append(r.get(key, {}).get("n_scored"))
        match.append(n_true.get(r["name"]) is not None
                     and n_mine_ev.get(r["name"]) == n_true.get(r["name"]))
    mine = np.array(mine)
    match = np.array(match)
    ok = ~np.isnan(mine)

    print("=== %s / %s, reading %s ===" % (split, model, key))
    print("paper method column: %s" % method)
    print("%-34s %8s %8s %8s %6s" % ("subset", "ours", "theirs", "diff", "n"))
    for label, sel in (("all proteins", ok),
                       ("scored-count reproduced exactly", ok & match),
                       ("scored-count NOT reproduced", ok & ~match)):
        if sel.sum() == 0:
            continue
        print("%-34s %8.3f %8.3f %+8.3f %6d"
              % (label, np.median(mine[sel]), np.median(theirs[sel]),
                 np.median(mine[sel]) - np.median(theirs[sel]), sel.sum()))

    d = mine[ok] - theirs[ok]
    print("\nper-protein (ours - theirs): mean %+.2f  median %+.2f  sd %.2f" %
          (d.mean(), np.median(d), d.std()))
    print("fraction where ours is higher: %.0f%%" % (100.0 * (d > 0).mean()))
    q = np.percentile(d, [5, 25, 50, 75, 95])
    print("percentiles 5/25/50/75/95: " + "  ".join("%+.1f" % x for x in q))

    small = np.array([n if n else 0 for n in ns])[ok]
    print("\nby size of the scored set:")
    for lo, hi in ((1, 10), (11, 20), (21, 30), (31, 10 ** 6)):
        s = (small >= lo) & (small <= hi)
        if s.sum():
            print("  n_scored %-8s ours %6.2f  theirs %6.2f  diff %+6.2f  (%d proteins)"
                  % ("%d-%d" % (lo, min(hi, 999)), np.median(mine[ok][s]),
                     np.median(theirs[ok][s]),
                     np.median(mine[ok][s]) - np.median(theirs[ok][s]), s.sum()))


if __name__ == "__main__":
    sys.exit(main())
