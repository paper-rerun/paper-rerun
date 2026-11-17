"""Find which reference-force filter on the test set reproduces Table 1's counts and Table S1.

Issue #7 reports 221 test configurations more than Table 1 says. This sweeps a
maximum reference force cut and prints the surviving counts and the resulting MAE,
so the cut that lands on 33884 / 13896 can be read off instead of guessed.
"""
import csv
import os
import sys

import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PAPER = {
    "small": {"PubChem": (33884, 1.41, 35.68), "DES370K Monomers": (889, 1.04, 17.63),
              "DES370K Dimers": (13896, 0.98, 16.31), "Dipeptides": (1025, 0.84, 25.07),
              "Solvated Amino Acids": (52, 1.60, 38.56), "water": (84, 1.67, 28.53),
              "QMugs": (144, 1.03, 41.45)},
    "medium": {"PubChem": (33884, 0.91, 20.57), "DES370K Monomers": (889, 0.63, 9.36),
               "DES370K Dimers": (13896, 0.58, 9.02), "Dipeptides": (1025, 0.52, 14.27),
               "Solvated Amino Acids": (52, 1.21, 23.26), "water": (84, 0.76, 15.27),
               "QMugs": (144, 0.69, 23.58)},
    "large": {"PubChem": (33884, 0.88, 14.75), "DES370K Monomers": (889, 0.59, 6.58),
              "DES370K Dimers": (13896, 0.54, 6.62), "Dipeptides": (1025, 0.42, 10.19),
              "Solvated Amino Acids": (52, 0.98, 19.43), "water": (84, 0.83, 13.57),
              "QMugs": (144, 0.45, 16.93)},
}


def load(key):
    by = {}
    with open(os.path.join(ROOT, "runs", "out", f"errors_{key}.csv"), newline="") as fh:
        for r in csv.DictReader(fh):
            by.setdefault(r["config_type"], []).append([
                int(r["n_atoms"]), float(r["abs_e_err_per_atom_eV"]),
                float(r["sum_abs_f_comp_err_eV_A"]), float(r["sum_abs_f_vec_err_eV_A"]),
                float(r["ref_max_abs_f_eV_A"]), float(r["ref_sum_f_norm_eV_A"]),
            ])
    return {k: np.array(v) for k, v in by.items()}


def agg(a):
    return len(a), a[:, 1].mean() * 1000, a[:, 2].sum() / (3 * a[:, 0].sum()) * 1000, \
        a[:, 3].sum() / a[:, 0].sum() * 1000


def main():
    keys = [k for k in ("small", "medium", "large")
            if os.path.exists(os.path.join(ROOT, "runs", "out", f"errors_{k}.csv"))]

    # Which cut lands on the published counts? Only needs one model's file.
    a = load(keys[0])
    print("# sweep of the maximum reference force cut, counts only")
    print(f"{'cut (eV/A)':>10s} " + " ".join(f"{s[:12]:>13s}" for s in sorted(a)))
    print(f"{'published':>10s} " + " ".join(
        f"{PAPER[keys[0]][s][0]:>13d}" for s in sorted(a)))
    for cut in (None, 50, 20, 15, 12, 11, 10.5, 10, 9.5, 9):
        row = []
        for s in sorted(a):
            v = a[s]
            row.append(len(v) if cut is None else int((v[:, 4] <= cut).sum()))
        label = "no cut" if cut is None else f"{cut}"
        print(f"{label:>10s} " + " ".join(f"{x:>13d}" for x in row))

    print("\n# Table S1 MAE, released file as is and with the 10 eV/A cut")
    for key in keys:
        d = load(key)
        print(f"\n## MACE-OFF23 {key}")
        print(f"{'subset':22s} {'n':>6s} {'n10':>6s} {'E_all':>7s} {'E_10':>7s} {'E_pap':>6s} "
              f"{'F_all':>8s} {'F_10':>8s} {'F_pap':>7s} {'Fvec_10':>8s}")
        for s in sorted(d):
            v = d[s]
            n0, e0, f0, _ = agg(v)
            n1, e1, f1, fv1 = agg(v[v[:, 4] <= 10.0])
            np_, ep, fp = PAPER[key][s]
            print(f"{s:22s} {n0:6d} {n1:6d} {e0:7.3f} {e1:7.3f} {ep:6.2f} "
                  f"{f0:8.3f} {f1:8.3f} {fp:7.2f} {fv1:8.3f}")


if __name__ == "__main__":
    main()
