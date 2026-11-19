"""Verify the defect claims independently before any of them is published.

C: which axis carries intensity, measured from the clean volume
D: fp goes negative when one label fills the crop, scoring a correct match 0
E: the ground truth is degenerate for short lengths, lv5 included
F: the noise is half-normal plus a background offset
"""
import io, os, sys
import numpy as np
import tifffile
from scipy import ndimage as ndi

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "repo", "nellie-supplemental", "outputs")
sys.path.insert(0, os.path.join(ROOT, "repo", "nellie-supplemental"))
from comparisons.simulations.multi_grid.analysis import check_IoU  # noqa: E402
from comparisons.simulations.multi_grid.multi_grid import (  # noqa: E402
    create_skeleton_sub_volume, populate_skeleton)
from comparisons.simulations.utils import add_noise  # noqa: E402

L = []

L += ["C - which axis carries intensity in the clean volume", ""]
im = tifffile.imread(os.path.join(OUT, "noiseless", "no_noise.ome.tif"))[5:-5, 5:-5, 5:-5]
st = im.shape[1] // 10
peak = np.zeros((10, 10, 10))
vox = np.zeros((10, 10, 10))
for a in range(10):
    for b in range(10):
        for c in range(10):
            cell = im[a*st+1:(a+1)*st-1, b*st+1:(b+1)*st-1, c*st+1:(c+1)*st-1]
            peak[a, b, c] = cell.max()
            vox[a, b, c] = (cell > 0).sum()
for ax in (0, 1, 2):
    others = tuple(x for x in (0, 1, 2) if x != ax)
    pm, vm = peak.mean(axis=others), vox.mean(axis=others)
    L.append("axis %d: peak %.0f..%.0f (range %.0f)   voxels %.0f..%.0f (range %.0f)"
             % (ax, pm[0], pm[-1], pm.max() - pm.min(), vm[0], vm[-1], vm.max() - vm.min()))
L.append("the generator's intensity_vector runs 6553 -> 58982")
L.append("check_IoU names its axes [thickness, intensity, length];"
         " visualize.py slices [:, level, :] and calls that an intensity level")
del im

L += ["", "D - fp goes negative when one label fills the section crop", ""]
gt = np.zeros((510, 510, 510), dtype=np.uint16)
gt[100:140, 100:140, 100:140] = 1
gtl, _ = ndi.label(gt)
out = np.zeros_like(gt, dtype=np.int32)
out[100:140, 100:140, 100:140] = 7          # one label, exactly on the object
f1a, ioua = check_IoU(gtl, out, is_label=True)
out_full = np.ones_like(gt, dtype=np.int32) * 7   # the same label fills every crop
f1b, ioub = check_IoU(gtl, out_full, is_label=True)
L.append("output = one label on the object:      f1 %.4f  iou %.4f"
         % (f1a[2, 2, 2], ioua[2, 2, 2]))
L.append("output = that label filling the crop:  f1 %.4f  iou %.4f"
         % (f1b[2, 2, 2], ioub[2, 2, 2]))
L.append("fp = len(unique[unique != tp_label]) - 1 assumes label 0 is present in the crop")
del gt, gtl, out, out_full

L += ["", "E - is the ground truth geometry degenerate at short lengths, lv5 included", ""]
px = 0.1
length_vector = np.linspace((0.2 * 2) / px, 40, 10)
thickness_px = np.linspace(0.2 * 2, 1, 10) / px
for i in (0, 3, 5, 7, 9):
    length = max(length_vector[i], thickness_px[0])
    sv = create_skeleton_sub_volume(length=length)
    c = np.argwhere(sv)
    L.append("length level %d (%.1f px): axis1 spans %d..%d, axis2 spans %d..%d  -> %s"
             % (i, length_vector[i], c[:, 1].min(), c[:, 1].max(),
                c[:, 2].min(), c[:, 2].max(),
                "straight rod pinned in the corner" if c[:, 1].max() == c[:, 1].min()
                else "curved"))
L.append("create_skeleton_sub_volume clips with np.clip(y, 0, length-1), not the 50-voxel cell")
L.append("the exported series is lv5")

L += ["", "F - is the added noise Gaussian, or half-normal plus an offset", ""]
small = np.zeros((40, 40, 40), dtype=np.uint16)
sigma_psf = (0.2 / px) / (2 * np.sqrt(2 * np.log(2)))
for std in (256, 8192, 32768):
    n = add_noise(small, psf_sigma=sigma_psf, gaussian_mean=0, gaussian_std=std,
                  apply_poisson=True).astype("float64")
    L.append("nominal std %5d -> added mean %8.1f  sd %8.1f   (std/sqrt(2pi) = %8.1f)"
             % (std, n.mean(), n.std(), std / np.sqrt(2 * np.pi)))
L.append("utils.add_noise clips the noise, not the noisy frame")

io.open(os.path.join(ROOT, "runs", "logs", "verify_defects.log"), "w",
        encoding="utf-8", newline="\n").write("\n".join(L) + "\n")
