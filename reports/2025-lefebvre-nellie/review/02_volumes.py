"""Axis identity in the generated grid, the frozen gate, and the separation the
report said it could not do: which zero cells are the 100-label shortcut's.

Reads one timepoint at a time through zarr; nothing is regenerated or re-segmented.
"""
import io, os, sys
import numpy as np
import tifffile
import zarr
from scipy import ndimage as ndi

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "repo", "nellie-supplemental", "outputs")
NELLIE = os.path.join(OUT, "nellie_output", "nellie_necessities")
LEVELS = [8, 1024, 8192, 32768]
out = []
P = out.append

noiseless = tifffile.imread(os.path.join(OUT, "noiseless", "no_noise.ome.tif"))
P("noiseless volume shape %s dtype %s" % (noiseless.shape, noiseless.dtype))
P("marked voxels (> 0): %d" % int((noiseless > 0).sum()))
lab, n = ndi.label(noiseless)
P("connected components (default connectivity): %d" % n)
lab27, n27 = ndi.label(noiseless, structure=np.ones((3, 3, 3)))
P("connected components (full 3x3x3): %d" % n27)

# --- which axis carries intensity? check_IoU calls axis 1 'intensity', axis 2 'length'
crop = noiseless[5:-5, 5:-5, 5:-5]
st = crop.shape[1] // 10
peak = np.zeros((10, 10, 10))
size = np.zeros((10, 10, 10))
for a in range(10):
    for b in range(10):
        for c in range(10):
            cell = crop[a*st+1:(a+1)*st-1, b*st+1:(b+1)*st-1, c*st+1:(c+1)*st-1]
            peak[a, b, c] = cell.max()
            size[a, b, c] = (cell > 0).sum()
P("")
P("per-cell peak intensity, marginal means along each axis of check_IoU's array")
for ax, name in ((0, "axis0 (check_IoU: thickness)"), (1, "axis1 (check_IoU: intensity)"),
                 (2, "axis2 (check_IoU: length)")):
    m = peak.mean(axis=tuple(x for x in (0, 1, 2) if x != ax))
    P("  %-32s peak %s" % (name, np.round(m, 0).astype(int).tolist()))
for ax, name in ((0, "axis0"), (1, "axis1"), (2, "axis2")):
    m = size.mean(axis=tuple(x for x in (0, 1, 2) if x != ax))
    P("  %-32s voxels %s" % (name, np.round(m, 0).astype(int).tolist()))
P("  intensity_vector in multi_grid.py: %s"
  % np.round(np.linspace(6553, 58982, 10)).astype(int).tolist())
del lab, lab27, crop, noiseless

# --- per-cell unique label counts from the segmentations, t0 only
P("")
P("per-cell label counts in nellie's output, t0: how many cells hit the >=100 shortcut")
for std in LEVELS:
    base = "gaussian_std_%d.ome" % std
    hit = sorted(f for f in os.listdir(NELLIE)
                 if base in f and f.endswith("skel_relabelled.ome.tif"))[0]
    with tifffile.TiffFile(os.path.join(NELLIE, hit)) as tf:
        store = tf.series[0].aszarr()
        im = np.asarray(zarr.open(store, mode="r")[0])
        store.close()
    im = im[5:-5, 5:-5, 5:-5]
    st = im.shape[1] // 10
    counts = np.zeros((10, 10, 10), dtype=np.int64)
    for a in range(10):
        for b in range(10):
            for c in range(10):
                cell = im[a*st+1:(a+1)*st-1, b*st+1:(b+1)*st-1, c*st+1:(c+1)*st-1]
                counts[a, b, c] = len(np.unique(cell))
    del im
    np.savez(os.path.join(ROOT, "review", "labelcount_%d_t0.npz" % std), counts=counts)
    z = np.load(os.path.join(ROOT, "runs", "out", "grid_%d_t0.npz" % std))
    f1, iou = z["f1"], z["iou"]
    short = counts >= 100
    zero_both = (f1 == 0) & (iou == 0)
    P("  std %5d: cells with >=100 labels %3d | f1=0 & iou=0 %3d | of those, shortcut %3d,"
      " genuinely missed %3d" % (std, int(short.sum()), int(zero_both.sum()),
                                 int((zero_both & short).sum()),
                                 int((zero_both & ~short).sum())))
    P("           shortcut cells not scored zero: %d (should be 0)"
      % int((short & ~zero_both).sum()))
    P("           max labels in a cell %d, median %d" % (counts.max(), int(np.median(counts))))
    sys.stdout.write("done %d\n" % std); sys.stdout.flush()

io.open(os.path.join(ROOT, "review", "02_volumes.log"), "w", encoding="utf-8",
        newline="\n").write("\n".join(out) + "\n")
