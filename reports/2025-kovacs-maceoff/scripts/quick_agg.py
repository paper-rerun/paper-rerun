"""Aggregate one per-config CSV by config_type. Used for the speed-test sanity check."""
import csv
import sys
from collections import defaultdict

rows = defaultdict(lambda: [0, 0.0, 0.0, 0.0])
with open(sys.argv[1], newline="") as fh:
    for r in csv.DictReader(fh):
        a = rows[r["config_type"]]
        a[0] += 1
        a[1] += int(r["n_atoms"])
        a[2] += float(r["abs_e_err_per_atom_eV"])
        a[3] += float(r["sum_abs_f_comp_err_eV_A"])
for k, (n, nat, se, sf) in sorted(rows.items()):
    print(f"{k:24s} n={n:6d}  E={1000 * se / n:7.3f} meV/atom  F={1000 * sf / (3 * nat):8.3f} meV/A")
