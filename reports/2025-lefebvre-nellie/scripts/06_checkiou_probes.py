"""Two defects in the authors' check_IoU, each shown on a hand-built case.

Probe A: the candidate test. check_IoU decides whether a label overlaps the ground truth
with `np.sum(np.isin(gt_coords, label_coords).all(axis=1)) == 0`. np.isin is elementwise
over the whole array, not a row lookup, so a coordinate counts as present when each of its
three numbers appears somewhere in label_coords, in any column, from any row. Two objects
that never touch can pass.

Probe B: the 100-label shortcut. `if len(unique_labels) < 100: # skip this, it's bad`
skips the whole matching loop when a cell holds 100 or more labels. tp_label stays None,
so the cell is scored f1 = 0 and max_iou = 0 even when one of those labels is a near
perfect match. The shortcut is a cost guard, but it reads as a measurement, and it only
fires in the noisy levels, which is where the curve falls.
"""
import numpy as np

print("Probe A - the candidate test accepts disjoint objects")
gt_coords = np.array([[1, 2, 3]])
label_coords = np.array([[3, 1, 9], [7, 2, 8]])  # no row equals [1, 2, 3]
hit = np.sum(np.isin(gt_coords, label_coords).all(axis=1))
rows_really_shared = sum(1 for r in gt_coords if any((r == l).all() for l in label_coords))
print("  gt coordinate [1 2 3], label coordinates", label_coords.tolist())
print("  rows actually shared:", rows_really_shared)
print("  what check_IoU counts:", int(hit), "-> treated as overlapping" if hit else "")
assert rows_really_shared == 0 and hit > 0, "probe A did not reproduce"

print()
print("Probe B - the 100-label shortcut zeroes a cell that holds a perfect match")
gt = np.zeros((20, 20, 20), dtype=np.uint16)
gt[8:12, 8:12, 8:12] = 1
for n_extra, expect in ((50, "scored"), (120, "zeroed")):
    lab = np.zeros_like(gt, dtype=np.int32)
    lab[8:12, 8:12, 8:12] = 1  # an exact copy of the ground truth object
    rng = np.random.default_rng(0)
    placed = 0
    while placed < n_extra:
        z, y, x = rng.integers(0, 20, 3)
        if lab[z, y, x] == 0:
            lab[z, y, x] = placed + 2
            placed += 1
    uniq = np.unique(lab)
    if len(uniq) < 100:
        best = max(
            np.logical_and(gt, lab == l).sum() / np.logical_or(gt, lab == l).sum()
            for l in uniq if l != 0)
    else:
        best = 0.0  # the shortcut: loop skipped, tp_label stays None
    print("  %3d extra labels -> %d unique, max_iou %.3f (%s)"
          % (n_extra, len(uniq), best, expect))
    assert (best > 0.9) == (n_extra == 50), "probe B did not reproduce"

print()
print("both probes reproduced")
