"""Replicate spread on the lv5 slice, which is the population the published row covers."""
import io, os, glob, re
import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REF = os.path.join(ROOT, "data", "ref", "seg_sim_exported_data")


def rows(metric, method="nellie"):
    fn = ("Multigrid_F1_lv5_%s.txt" if metric == "f1" else "IoU_Multigrid_F1_lv5_%s.txt") % method
    out = {}
    for line in io.open(os.path.join(REF, fn), encoding="utf-8").read().splitlines()[1:]:
        p = line.split("\t")
        out[int(p[0])] = (float(p[1]), float(p[2]), int(p[3]))
    return out


L = ["full published rows for the two baselines we ran", ""]
for method in ("otsu", "triangle"):
    for metric in ("f1", "iou"):
        r = rows(metric, method)
        L.append("%-8s %-4s " % (method, metric) + " ".join(
            "%d:%.4f" % (k, r[k][0]) for k in sorted(r)))

L += ["", "our lv5 slice, both noise draws, against print", ""]
L.append("level  metric   draw 0   draw 1   sd across draws   published        sd printed")
for std in (8, 1024, 8192, 32768):
    for metric in ("f1", "iou"):
        vals = []
        for t in (0, 1):
            z = np.load(os.path.join(ROOT, "runs", "out", "grid_%d_t%d.npz" % (std, t)))
            vals.append(float(z[metric][:, 5, :].mean()))
        pm, ps, _ = rows(metric)[std]
        L.append("%5d  %-6s   %.4f   %.4f   %.4f            %.4f           %.4f"
                 % (std, metric, vals[0], vals[1], np.std(vals, ddof=1), pm, ps))

L += ["", "our per-cell sd over the 100 cells of the slice, which is what visualize.py computes", ""]
L.append("level  metric   our sd (100 cells)   sd printed   ratio")
for std in (8, 1024, 8192, 32768):
    for metric in ("f1", "iou"):
        z = np.load(os.path.join(ROOT, "runs", "out", "grid_%d_t0.npz" % std))
        s = float(z[metric][:, 5, :].std())
        ps = rows(metric)[std][1]
        L.append("%5d  %-6s   %.4f               %.4f       %s"
                 % (std, metric, s, ps, "%.2f" % (s / ps) if ps > 0 else "n/a"))

io.open(os.path.join(ROOT, "runs", "logs", "slice_spread.log"), "w",
        encoding="utf-8", newline="\n").write("\n".join(L) + "\n")
