"""Does the >=100 label shortcut fire for the threshold controls? Nellie never reaches it.

Counted per cell by labelling the 48^3 cell block alone (check_IoU labels the whole 500^3
crop and then slices, so a structure crossing the gap between cells is one label there and
two here; for isolated noise specks the two counts agree).
"""
import io, os
import numpy as np
import tifffile
from scipy import ndimage as ndi

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "repo", "nellie-supplemental", "outputs")
out = []
P = out.append
S = np.ones((3, 3, 3))

for method in ("otsu", "triangle"):
    for std in (8, 1024, 8192, 32768):
        path = os.path.join(OUT, method, "gaussian_std_%d.ome.tif" % std)
        if not os.path.exists(path):
            P("missing %s" % path)
            continue
        import zarr
        with tifffile.TiffFile(path) as tf:
            store = tf.series[0].aszarr()
            z = zarr.open(store, mode="r")
            vol = z[0] if len(z.shape) == 4 else z
            counts = np.zeros((10, 10, 10), dtype=np.int64)
            for a in range(10):
                z0 = 5 + a * 50
                slab = np.asarray(vol[z0+1:z0+49])  # one row of cells at a time
                for b in range(10):
                    for c in range(10):
                        y0, x0 = 5 + b * 50, 5 + c * 50
                        cell = slab[:, y0+1:y0+49, x0+1:x0+49]
                        _, k = ndi.label(cell, structure=S)
                        counts[a, b, c] = k + 1  # +1 for background, as np.unique sees it
                del slab
            store.close()
        P("%-8s std %5d: cells with >=100 labels %4d of 1000  median %5d  max %5d"
          % (method, std, int((counts >= 100).sum()), int(np.median(counts)), counts.max()))
        np.savez(os.path.join(ROOT, "review", "labelcount_%s_%d_t0.npz" % (method, std)),
                 counts=counts)
        print(method, std, "done", flush=True)

io.open(os.path.join(ROOT, "review", "03_otsu_shortcut.log"), "w", encoding="utf-8",
        newline="\n").write("\n".join(out) + "\n")
