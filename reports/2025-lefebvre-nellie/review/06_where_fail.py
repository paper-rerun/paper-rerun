"""Where in the grid do our cells fail, and with how many labels? axis0=thickness,
axis1=length, axis2=intensity (as the generator writes them)."""
import io, os
import numpy as np
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
out = []
P = out.append
NAME = {0: "thickness", 1: "length(ax1)", 2: "intensity(ax2)"}
for std in (8, 1024, 8192, 32768):
    z = np.load(os.path.join(ROOT, "runs", "out", "grid_%d_t0.npz" % std))
    f1, iou = z["f1"], z["iou"]
    counts = np.load(os.path.join(ROOT, "review", "labelcount_%d_t0.npz" % std))["counts"]
    bad = f1 < 1
    P("std %d: %d cells with f1<1, %d with f1==0, %d with iou==0"
      % (std, int(bad.sum()), int((f1 == 0).sum()), int((iou == 0).sum())))
    for ax in (0, 1, 2):
        P("   f1<1 per %-14s %s" % (NAME[ax], bad.sum(axis=tuple(x for x in (0,1,2) if x != ax)).tolist()))
    P("   label count in failing cells: min %d median %d max %d"
      % (counts[bad].min(), int(np.median(counts[bad])), counts[bad].max()) if bad.any() else "   none")
    P("   mean f1 per thickness index: %s" % np.round(f1.mean(axis=(1, 2)), 3).tolist())
    P("   mean iou per intensity index (ax2): %s" % np.round(iou.mean(axis=(0, 1)), 3).tolist())
io.open(os.path.join(ROOT, "review", "06_where_fail.log"), "w", encoding="utf-8",
        newline="\n").write("\n".join(out) + "\n")
print("\n".join(out))
