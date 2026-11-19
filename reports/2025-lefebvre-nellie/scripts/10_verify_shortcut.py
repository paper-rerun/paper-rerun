"""Who actually trips the 100-label shortcut, and which length levels are degenerate.

The shortcut `if len(unique_labels) < 100` only fires when a section crop holds 100 or
more labels. Count labels per crop the way check_IoU does - global labelling with full
26-connectivity for a binary input, the stored labels for Nellie - and see which method
and which level reaches it.
"""
import io, os, sys
import numpy as np
import tifffile
from scipy import ndimage as ndi

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "repo", "nellie-supplemental", "outputs")
NELLIE = os.path.join(OUT, "nellie_output", "nellie_necessities")
sys.path.insert(0, os.path.join(ROOT, "repo", "nellie-supplemental"))
from comparisons.simulations.multi_grid.multi_grid import create_skeleton_sub_volume  # noqa: E402

L = ["E2 - every length level, degenerate or curved", ""]
length_vector = np.linspace((0.2 * 2) / 0.1, 40, 10)
thin = np.linspace(0.2 * 2, 1, 10)[0] / 0.1
degenerate = []
for i in range(10):
    sv = create_skeleton_sub_volume(length=max(length_vector[i], thin))
    c = np.argwhere(sv)
    span = int(c[:, 1].max() - c[:, 1].min())
    if span == 0:
        degenerate.append(i)
    L.append("level %d (%4.1f px): curvature span %2d voxels -> %s"
             % (i, length_vector[i], span, "DEGENERATE rod" if span == 0 else "curved"))
L.append("degenerate levels: %s   the exported series is lv5" % degenerate)

L += ["", "G - labels per section crop, and who reaches 100", ""]
L.append("method    level   max labels in a crop   crops with >=100   of 1000")


def counts(arr):
    arr = arr[5:-5, 5:-5, 5:-5]
    st = arr.shape[1] // 10
    mx, over = 0, 0
    for a in range(10):
        for b in range(10):
            for c in range(10):
                u = len(np.unique(arr[a*st+1:(a+1)*st-1, b*st+1:(b+1)*st-1, c*st+1:(c+1)*st-1]))
                mx = max(mx, u)
                over += u >= 100
    return mx, over


for std in (8, 1024, 8192, 32768):
    base = "gaussian_std_%d.ome" % std
    hit = sorted(f for f in os.listdir(NELLIE)
                 if base in f and f.endswith("skel_relabelled.ome.tif"))[0]
    with tifffile.TiffFile(os.path.join(NELLIE, hit)) as tf:
        import zarr
        store = tf.series[0].aszarr()
        arr = np.asarray(zarr.open(store, mode="r")[0])
        store.close()
    mx, over = counts(arr)
    L.append("nellie  %6d   %18d   %16d   of 1000" % (std, mx, over))
    del arr

for name in ("otsu", "triangle"):
    d = os.path.join(OUT, name)
    for std in (8, 1024, 8192, 32768):
        p = os.path.join(d, "gaussian_std_%d.ome.tif" % std)
        if not os.path.exists(p):
            continue
        im = tifffile.imread(p)
        if im.ndim == 4:
            im = im[0]
        lab, _ = ndi.label(im, structure=np.ones((3, 3, 3)))   # as check_IoU does
        del im
        mx, over = counts(lab)
        L.append("%-7s %6d   %18d   %16d   of 1000" % (name, std, mx, over))
        del lab

L.append("")
L.append("published rows for the baselines, for comparison:")
for metric, fn in (("f1", "Multigrid_F1_lv5_%s.txt"), ("iou", "IoU_Multigrid_F1_lv5_%s.txt")):
    for name in ("otsu", "triangle"):
        path = os.path.join(ROOT, "data", "ref", "seg_sim_exported_data", fn % name)
        if not os.path.exists(path):
            continue
        rows = {}
        for line in io.open(path, encoding="utf-8").read().splitlines()[1:]:
            p = line.split("\t")
            rows[int(p[0])] = (p[1], p[2])
        L.append("  %-8s %-4s " % (name, metric) + "  ".join(
            "%d: %s+-%s" % (k, rows[k][0][:6], rows[k][1][:6])
            for k in (2048, 4096, 8192, 16384, 32768) if k in rows))

io.open(os.path.join(ROOT, "runs", "logs", "verify_shortcut.log"), "w",
        encoding="utf-8", newline="\n").write("\n".join(L) + "\n")
