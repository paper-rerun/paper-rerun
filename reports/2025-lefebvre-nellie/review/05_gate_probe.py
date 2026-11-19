"""Does the broken candidate gate (finding 4) change any score? Compare the authors'
check_IoU against the same function with the gate fixed to a real row lookup.
"""
import io, os, sys
import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "repo", "nellie-supplemental"))
from comparisons.simulations.multi_grid.analysis import check_IoU  # noqa: E402
import comparisons.simulations.multi_grid.analysis as A  # noqa: E402

src = io.open(A.__file__, encoding="utf-8").read()
fixed_src = src.replace(
    "if np.sum(np.isin(gt_partial_coords, label_coords).all(axis=1)) == 0:",
    "if not (set(map(tuple, gt_partial_coords)) & set(map(tuple, label_coords))):")
assert fixed_src != src
ns = {}
exec(compile(fixed_src.split("if __name__")[0], "fixed", "exec"), ns)
check_IoU_fixed = ns["check_IoU"]

rng = np.random.default_rng(7)
out = []
P = out.append
P("same 10x10x10 grid, authors' gate vs a row-lookup gate, over random scenes")
for trial in range(6):
    gt = np.zeros((100, 100, 100), dtype=np.int32)
    lab = np.zeros_like(gt)
    k = 0
    for a in range(10):
        for b in range(10):
            for c in range(10):
                k += 1
                z, y, x = a * 10 + 2, b * 10 + 2, c * 10 + 2
                gt[z:z+5, y:y+5, x:x+5] = k
                mode = rng.integers(0, 4)
                if mode == 0:           # exact match
                    lab[z:z+5, y:y+5, x:x+5] = k
                elif mode == 1:         # partial overlap plus a disjoint intruder
                    lab[z:z+3, y:y+3, x:x+3] = k
                    lab[z+6, y+6, x+6] = 1000 + k
                elif mode == 2:         # only a disjoint label, placed to pass the broken gate
                    lab[z+6:z+8, y+6:y+8, x+6:x+8] = 2000 + k
                # mode 3: nothing
    f1a, ioua = check_IoU(gt, lab, is_label=True)
    f1b, ioub = check_IoU_fixed(gt, lab, is_label=True)
    P("  trial %d  f1 identical %s  iou identical %s  mean f1 %.4f  mean iou %.4f"
      % (trial, np.array_equal(f1a, f1b), np.allclose(ioua, ioub), f1a.mean(), ioua.mean()))

P("")
P("and the gate itself: how often it lets a non-overlapping label through")
gt_c = np.argwhere(np.ones((5, 5, 5)))
lab_c = np.argwhere(np.ones((5, 5, 5))) + 6   # disjoint, but every value appears somewhere
P("  broken gate says overlap: %d coords" % int(np.sum(np.isin(gt_c, lab_c).all(axis=1))))
P("  rows really shared: %d" % len(set(map(tuple, gt_c)) & set(map(tuple, lab_c))))
io.open(os.path.join(ROOT, "review", "05_gate_probe.log"), "w", encoding="utf-8",
        newline="\n").write("\n".join(out) + "\n")
print("\n".join(out))
