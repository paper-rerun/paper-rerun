"""Measure the spread across independent noise draws, which the paper never reports.

multi_grid.py writes three timepoints per file, each an independent noise draw over the
same clean volume (`for t in range(3)` with no seed). The authors' run recipe reads only
the first (`select_temporal_range(0, 1)`), and their analysis.py takes `[0]`, so the other
two are never touched. Segmenting them gives the only replicate spread the release can
support, which is what a reader takes "mean +- sd, N=10" to mean.

One level per call, one timepoint per call: the volumes are 1 GB and memory is not
released between stages inside a process.
"""
import io, json, os, sys, time
import numpy as np
import tifffile
from scipy import ndimage as ndi

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "repo", "nellie-supplemental", "outputs")
NELLIE = os.path.join(OUT, "nellie_output", "nellie_necessities")
sys.path.insert(0, os.path.join(ROOT, "repo", "nellie-supplemental"))

from comparisons.simulations.multi_grid.analysis import check_IoU  # noqa: E402
from nellie.im_info.verifier import FileInfo, ImInfo  # noqa: E402
from nellie.segmentation.filtering import Filter  # noqa: E402
from nellie.segmentation.labelling import Label  # noqa: E402
from nellie.segmentation.networking import Network  # noqa: E402

STD = int(sys.argv[1])
T = int(sys.argv[2])
tag = "t%d_to_%d" % (T, T + 1)
path = os.path.join(OUT, "gaussian_std_%d.ome.tif" % STD)

hits = [f for f in os.listdir(NELLIE)
        if ("gaussian_std_%d.ome" % STD) in f and tag in f
        and f.endswith("skel_relabelled.ome.tif")]
if not hits:
    t0 = time.time()
    file_info = FileInfo(path)
    file_info.find_metadata()
    file_info.load_metadata()
    file_info.select_temporal_range(T, T + 1)
    im_info = ImInfo(file_info)
    Filter(im_info, remove_edges=False).run()
    Label(im_info).run()
    Network(im_info).run()
    print("std %d t%d segmented in %.1f s" % (STD, T, time.time() - t0), flush=True)
    hits = [f for f in os.listdir(NELLIE)
            if ("gaussian_std_%d.ome" % STD) in f and tag in f
            and f.endswith("skel_relabelled.ome.tif")]

noiseless = tifffile.imread(os.path.join(OUT, "noiseless", "no_noise.ome.tif"))
noiseless_label, n = ndi.label(noiseless)
assert n == 1000, "frozen gate: want 1000 components, got %d" % n

im = tifffile.imread(os.path.join(NELLIE, sorted(hits)[0]))
if im.ndim == 4:
    im = im[0]
f1, iou = check_IoU(noiseless_label, im, is_label=True)
np.savez(os.path.join(ROOT, "runs", "out", "grid_%d_t%d.npz" % (STD, T)), f1=f1, iou=iou)
print("std %d t%d  f1 %.4f  iou %.4f" % (STD, T, f1.mean(), iou.mean()), flush=True)
