"""Measure the spread across independent noise draws, which the release does report but
nobody reads.

multi_grid.py writes three timepoints per file, each an independent Poisson + Gaussian
draw over the same clean volume, with no seed. FileInfo.select_temporal_range takes an
INCLUSIVE end (t_end defaults to shape - 1), so the authors' own recipe, (0, 1), already
segments two of them; their analysis.py then takes [0] and the second is discarded. So
the second draw is sitting in the files we already wrote, and the replicate spread costs
no segmentation at all.

That spread is what a reader takes "mean +- sd, N = 10" to mean. Read one timepoint at a
time through zarr: the series is 2 x 510^3 uint32, and loading both at once is 2 GB.
"""
import io, json, os, sys
import numpy as np
import tifffile
from scipy import ndimage as ndi

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "repo", "nellie-supplemental", "outputs")
NELLIE = os.path.join(OUT, "nellie_output", "nellie_necessities")
sys.path.insert(0, os.path.join(ROOT, "repo", "nellie-supplemental"))
from comparisons.simulations.multi_grid.analysis import check_IoU  # noqa: E402

LEVELS = [8, 1024, 8192, 32768]


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
del noiseless

grids = {}
for std in LEVELS:
    base = "gaussian_std_%d.ome" % std
    hit = sorted(f for f in os.listdir(NELLIE)
                 if base in f and f.endswith("skel_relabelled.ome.tif"))[0]
    for t in (0, 1):
        cache = os.path.join(ROOT, "runs", "out", "grid_%d_t%d.npz" % (std, t))
        if os.path.exists(cache):
            z = np.load(cache)
            grids[(std, t)] = {"f1": z["f1"], "iou": z["iou"]}
            continue
        with tifffile.TiffFile(os.path.join(NELLIE, hit)) as tf:
            store = tf.series[0].aszarr()
            import zarr
            im = np.asarray(zarr.open(store, mode="r")[t])
            store.close()
        f1, iou = check_IoU(noiseless_label, im, is_label=True)
        del im
        np.savez(cache, f1=f1, iou=iou)
        grids[(std, t)] = {"f1": f1, "iou": iou}
        print("measured std %d t%d" % (std, t), flush=True)

lines = ["level  metric  draw 0   draw 1   |diff|   sd across the 2 draws   sd printed (N=10)"]
summary = {}
for metric in ("f1", "iou"):
    pub = published(metric)
    for std in LEVELS:
        a = float(grids[(std, 0)][metric].mean())
        b = float(grids[(std, 1)][metric].mean())
        sd = float(np.std([a, b], ddof=1))
        ps = pub[std][1]
        summary["%s_%d" % (metric, std)] = {"draw0": a, "draw1": b, "sd_replicate": sd,
                                            "sd_printed": ps}
        lines.append("%5d  %-6s  %.4f   %.4f   %.4f   %.4f                 %.4f"
                     % (std, metric, a, b, abs(a - b), sd, ps))

# sigma=8 F1 prints sd 0, so it carries no ratio and is left out of this line
ratios = [v["sd_printed"] / v["sd_replicate"] for v in summary.values()
          if v["sd_replicate"] > 0 and v["sd_printed"] > 0]
lines.append("")
lines.append("On the seven pairs with a non-zero printed sd, the printed bar is %.0fx to %.0fx"
             " the spread between two independent draws." % (min(ratios), max(ratios)))
txt = "\n".join(lines) + "\n"
io.open(os.path.join(ROOT, "runs", "logs", "replicate_spread.log"), "w",
        encoding="utf-8", newline="\n").write(txt)
io.open(os.path.join(ROOT, "runs", "out", "replicate_spread.json"), "w",
        encoding="utf-8", newline="\n").write(json.dumps(summary, indent=1) + "\n")
print(txt)
