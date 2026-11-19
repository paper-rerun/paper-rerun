"""Global per-cell label counts for one control output, the way check_IoU counts them:
label the whole 500^3 crop with full connectivity, then count np.unique per cell.
One level per process; the int32 label volume is 500 MB.
"""
import io, os, sys
import numpy as np
import tifffile, zarr
from scipy import ndimage as ndi

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "repo", "nellie-supplemental", "outputs")
method, std = sys.argv[1], int(sys.argv[2])
path = os.path.join(OUT, method, "gaussian_std_%d.ome.tif" % std)
with tifffile.TiffFile(path) as tf:
    store = tf.series[0].aszarr()
    z = zarr.open(store, mode="r")
    vol = np.asarray(z[0] if len(z.shape) == 4 else z)[5:-5, 5:-5, 5:-5].astype(bool)
    store.close()
occ = float(vol.mean())
lab, n = ndi.label(vol, structure=np.ones((3, 3, 3)))
del vol
counts = np.zeros((10, 10, 10), dtype=np.int64)
for a in range(10):
    for b in range(10):
        for c in range(10):
            counts[a, b, c] = len(np.unique(lab[a*50+1:(a+1)*50-1, b*50+1:(b+1)*50-1,
                                                c*50+1:(c+1)*50-1]))
del lab
line = ("%-8s std %5d: occupancy %.4f  global labels %d  cells with >=100 labels %d of 1000"
        "  median %d  max %d" % (method, std, occ, n, int((counts >= 100).sum()),
                                 int(np.median(counts)), counts.max()))
print(line, flush=True)
with io.open(os.path.join(ROOT, "review", "04_global_labels.log"), "a",
             encoding="utf-8", newline="\n") as f:
    f.write(line + "\n")
