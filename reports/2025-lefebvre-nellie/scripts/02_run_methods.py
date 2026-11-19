"""Run Nellie 0.4.1 and the two cheap controls over the chosen noise levels.

The recipe is the authors' own, from the commented batch block at the bottom of
nellie/run.py: channel 0, one timepoint, remove_edges off.

We call their pipeline stages directly instead of their run(), and stop after Network.
Three reasons, all of them settled before seeing any number:

  - Network is the stage that writes im_skel_relabelled.ome.tif, which is the only file
    their analysis.py reads for the segmentation figure we are reproducing.
  - Tracking is explicitly not claimed in claims.json, and their own issue #49 reports a
    tracking regression between this version and main.
  - Hierarchy, the feature-extraction stage, did not complete here. On the first level it
    ran about 83 minutes past segmentation and then died trying to allocate 8.67 GiB for a
    19697 x 19697 x 3 pairwise distance array in _get_branch_stats. The traceback is in
    runs/logs/hierarchy_oom.log. It is reported, not worked around.

Otsu and Triangle come from the authors' otsu_triangle_only.py, imported rather than
reimplemented, with the same half-pixel Gaussian they apply before thresholding.

Four noise levels, fixed in claims.json before any of this ran: 8, 1024, 8192, 32768.
"""
import json, os, sys, time
import numpy as np
import tifffile
from scipy import ndimage as ndi

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "repo", "nellie-supplemental", "outputs")
NELLIE_OUT = os.path.join(OUT, "nellie_output", "nellie_necessities")
sys.path.insert(0, os.path.join(ROOT, "repo", "nellie-supplemental"))

from comparisons.segmentation_comparisons.otsu_triangle_only import (  # noqa: E402
    otsu_threshold, triangle_threshold)
from nellie.im_info.verifier import FileInfo, ImInfo  # noqa: E402
from nellie.segmentation.filtering import Filter  # noqa: E402
from nellie.segmentation.labelling import Label  # noqa: E402
from nellie.segmentation.networking import Network  # noqa: E402

LEVELS = [int(a) for a in sys.argv[1:]] or [8, 1024, 8192, 32768]
TIMINGS = os.path.join(ROOT, "runs", "out", "timings.json")
timings = json.load(open(TIMINGS)) if os.path.exists(TIMINGS) else {}


def already_segmented(std):
    if not os.path.isdir(NELLIE_OUT):
        return False
    tag = "gaussian_std_%d.ome-" % std
    return any(f.startswith(tag) and f.endswith("im_skel_relabelled.ome.tif")
               for f in os.listdir(NELLIE_OUT))


def control(path, name, fn):
    d = os.path.join(OUT, name)
    os.makedirs(d, exist_ok=True)
    dst = os.path.join(d, os.path.basename(path))
    if os.path.exists(dst):
        return "ja existia"
    t0 = time.time()
    im = np.asarray(tifffile.imread(path), dtype="float64")
    im = ndi.gaussian_filter(im, sigma=0.5)
    tifffile.imwrite(dst, im > fn(im))
    return round(time.time() - t0, 1)


for std in LEVELS:
    path = os.path.join(OUT, "gaussian_std_%d.ome.tif" % std)
    if not os.path.exists(path):
        print("FALTA", path, flush=True)
        continue
    key = str(std)
    timings.setdefault(key, {})["size_mb"] = round(os.path.getsize(path) / 1e6, 1)

    if already_segmented(std):
        print(std, "nellie ja rodou, pulando", flush=True)
        timings[key].setdefault("nellie_s", "ja existia")
    else:
        t0 = time.time()
        file_info = FileInfo(path)
        file_info.find_metadata()
        file_info.load_metadata()
        file_info.select_temporal_range(0, 1)
        im_info = ImInfo(file_info)
        Filter(im_info, remove_edges=False).run()
        Label(im_info).run()
        Network(im_info).run()
        timings[key]["nellie_s"] = round(time.time() - t0, 1)
        print(std, "nellie (ate Network)", timings[key]["nellie_s"], "s", flush=True)

    timings[key]["otsu_s"] = control(path, "otsu", lambda m: otsu_threshold(m)[0])
    timings[key]["triangle_s"] = control(path, "triangle", triangle_threshold)
    print(std, "controles ok", flush=True)

    with open(TIMINGS, "w", newline="\n") as f:
        json.dump(timings, f, indent=1)

print(json.dumps(timings, indent=1))
