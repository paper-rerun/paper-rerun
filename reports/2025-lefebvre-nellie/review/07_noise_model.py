"""Two properties of the authors' add_noise that the report does not mention.
Runs on a 21^3 toy array; nothing in the benchmark is regenerated."""
import io, os, sys
import numpy as np
import tifffile, zarr

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "repo", "nellie-supplemental"))
from comparisons.simulations.utils import add_noise  # noqa: E402

out = []
P = out.append
delta = np.zeros((21, 21, 21), dtype=np.uint16)
delta[10, 10, 10] = 60000
blurred = add_noise(delta, psf_sigma=0.85, gaussian_mean=0, gaussian_std=0, apply_poisson=False)
P("toy delta blurred by add_noise(psf_sigma=0.85), profiles through the peak")
P("  along axis0 (z): %s" % np.round(blurred[8:13, 10, 10]).astype(int).tolist())
P("  along axis1 (y): %s" % np.round(blurred[10, 8:13, 10]).astype(int).tolist())
P("  along axis2 (x): %s" % np.round(blurred[10, 10, 8:13]).astype(int).tolist())
P("  -> add_noise loops over the first axis of whatever it is given; multi_grid.py hands it")
P("     a 3D volume, so each z slice is blurred in 2D and there is no axial blur at all.")

flat = np.zeros((9, 64, 64), dtype=np.uint16)
noisy = add_noise(flat, psf_sigma=0, gaussian_mean=0, gaussian_std=32768, apply_poisson=False)
P("")
P("background of a zero volume at gaussian_std=32768, no Poisson:")
P("  mean %.0f  min %.0f  max %.0f  (a zero-mean normal would give mean 0)"
  % (noisy.mean(), noisy.min(), noisy.max()))
P("  sigma / sqrt(2*pi) = %.0f, the mean of a normal with its negative half set to zero"
  % (32768 / np.sqrt(2 * np.pi)))

path = os.path.join(ROOT, "repo", "nellie-supplemental", "outputs", "gaussian_std_32768.ome.tif")
with tifffile.TiffFile(path) as tf:
    store = tf.series[0].aszarr()
    slab = np.asarray(zarr.open(store, mode="r")[0, 0:3])
    store.close()
P("")
P("first 3 z slices of the real sigma=32768 file: mean %.0f  median %.0f  min %.0f"
  % (slab.mean(), np.median(slab), slab.min()))
io.open(os.path.join(ROOT, "review", "07_noise_model.log"), "w", encoding="utf-8",
        newline="\n").write("\n".join(out) + "\n")
print("\n".join(out))
