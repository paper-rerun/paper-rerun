"""Find which reduction of the 10x10x10 array reproduces the published mean and sd.

check_IoU returns f1_array[thickness, intensity, length]. The paper reports mean, sd, N=10
for every noise level, and nothing in the released code performs that last reduction, so
which of the three axes the 10 belongs to is unknown. This scans every candidate:
collapse along each axis in turn and take the sd across the 10 survivors, or ignore the
axes and take the sd across all 1000 cells. Scored by how far the sd lands from print.
"""
import io, json, os, sys
import numpy as np
import tifffile
from scipy import ndimage as ndi

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "repo", "nellie-supplemental", "outputs")
sys.path.insert(0, os.path.join(ROOT, "repo", "nellie-supplemental"))
from comparisons.simulations.multi_grid.analysis import check_IoU  # noqa: E402

LEVELS = [8, 1024, 8192, 32768]
AXIS_NAME = {0: "thickness", 1: "intensity", 2: "length"}


def published(metric):
    name = "Multigrid_F1_lv5_nellie.txt" if metric == "f1" else "IoU_Multigrid_F1_lv5_nellie.txt"
    rows = {}
    for line in io.open(os.path.join(ROOT, "data", "ref", "seg_sim_exported_data", name),
                        encoding="utf-8").read().splitlines()[1:]:
        p = line.split("\t")
        rows[int(p[0])] = (float(p[1]), float(p[2]), int(p[3]))
    return rows


noiseless = tifffile.imread(os.path.join(OUT, "noiseless", "no_noise.ome.tif"))
noiseless_label, n = ndi.label(noiseless)
assert n == 1000, "frozen gate: want 1000 components, got %d" % n

NELLIE = os.path.join(OUT, "nellie_output", "nellie_necessities")
arrays = {}
for std in LEVELS:
    base = "gaussian_std_%d.ome" % std
    hit = sorted(f for f in os.listdir(NELLIE)
                 if base in f and f.endswith("skel_relabelled.ome.tif"))[0]
    # Keep only the 10x10x10 grid and drop the 1 GB volume before reading the next one,
    # otherwise four of them at once exhaust the RAM on this machine
    cache = os.path.join(ROOT, "runs", "out", "grid_%d.npz" % std)
    if os.path.exists(cache):
        z = np.load(cache)
        arrays[std] = {"f1": z["f1"], "iou": z["iou"]}
        continue
    im = tifffile.imread(os.path.join(NELLIE, hit))
    if im.ndim == 4:
        im = im[0]
    f1, iou = check_IoU(noiseless_label, im, is_label=True)
    del im
    np.savez(cache, f1=f1, iou=iou)
    arrays[std] = {"f1": f1, "iou": iou}

cands = [("all 1000 cells", None)] + [("mean over %s" % AXIS_NAME[a], a) for a in (0, 1, 2)]
score = {c[0]: [] for c in cands}
lines = ["candidate            level  metric  our mean   our sd    pub mean   pub sd    d(sd)"]
for name, axis in cands:
    for metric in ("f1", "iou"):
        pub = published(metric)
        for std in LEVELS:
            arr = arrays[std][metric]
            if axis is None:
                m, s = float(arr.mean()), float(arr.std())
            else:
                red = arr.mean(axis=tuple(x for x in (0, 1, 2) if x != axis))
                m, s = float(red.mean()), float(red.std())
            pm, ps, _ = pub[std]
            score[name].append(abs(s - ps))
            lines.append("%-20s %6d  %-6s  %.4f    %.4f    %.4f    %.4f    %+.4f"
                         % (name, std, metric, m, s, pm, ps, s - ps))

lines.append("")
lines.append("mean |sd - published sd| over the 8 pairs, smaller is the better fit:")
for name, _ in cands:
    lines.append("  %-20s %.4f" % (name, float(np.mean(score[name]))))
txt = "\n".join(lines) + "\n"
io.open(os.path.join(ROOT, "runs", "logs", "aggregation_scan.log"), "w",
        encoding="utf-8", newline="\n").write(txt)
print(txt)
