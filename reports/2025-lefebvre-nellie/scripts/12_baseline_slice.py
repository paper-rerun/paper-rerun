"""Score the two baselines on the lv5 slice.

Otsu and Triangle share the regenerated volume, the ground truth, the noise draw and
check_IoU with our Nellie run. If their published rows come back and Nellie's does not,
the difference is in the segmenter and not in anything upstream of it.
"""
import io, os, sys
import numpy as np
import tifffile
from scipy import ndimage as ndi

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "repo", "nellie-supplemental", "outputs")
sys.path.insert(0, os.path.join(ROOT, "repo", "nellie-supplemental"))
from comparisons.simulations.multi_grid.analysis import check_IoU  # noqa: E402

REF = os.path.join(ROOT, "data", "ref", "seg_sim_exported_data")


def rows(metric, method):
    fn = ("Multigrid_F1_lv5_%s.txt" if metric == "f1" else "IoU_Multigrid_F1_lv5_%s.txt") % method
    out = {}
    for line in io.open(os.path.join(REF, fn), encoding="utf-8").read().splitlines()[1:]:
        p = line.split("\t")
        out[int(p[0])] = (float(p[1]), float(p[2]), int(p[3]))
    return out


noiseless = tifffile.imread(os.path.join(OUT, "noiseless", "no_noise.ome.tif"))
gt, n = ndi.label(noiseless)
assert n == 1000
del noiseless

L = ["method    level  metric   ours (slice)   published   delta", ""]
for method in ("otsu", "triangle"):
    for std in (8, 1024, 8192, 32768):
        p = os.path.join(OUT, method, "gaussian_std_%d.ome.tif" % std)
        if not os.path.exists(p):
            continue
        im = tifffile.imread(p)
        if im.ndim == 4:
            im = im[0]
        f1, iou = check_IoU(gt, im, is_label=False)
        del im
        np.savez(os.path.join(ROOT, "runs", "out", "grid_%s_%d.npz" % (method, std)),
                 f1=f1, iou=iou)
        for metric, arr in (("f1", f1), ("iou", iou)):
            o = float(arr[:, 5, :].mean())
            pm = rows(metric, method)[std][0]
            L.append("%-8s %6d  %-6s   %.4f         %.4f      %+.4f"
                     % (method, std, metric, o, pm, o - pm))
        print("done", method, std, flush=True)

io.open(os.path.join(ROOT, "runs", "logs", "baseline_slice.log"), "w",
        encoding="utf-8", newline="\n").write("\n".join(L) + "\n")
