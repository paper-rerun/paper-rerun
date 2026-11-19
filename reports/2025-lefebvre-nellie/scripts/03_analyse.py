"""Measure IoU and F1 with the authors' own check_IoU, then aggregate and compare.

check_IoU comes from their analysis.py, imported, not reimplemented. It returns a
10x10x10 array of per-object F1 and max-IoU, indexed [thickness, intensity, length].

The published Source Data has one row per noise level with N = 10, which their published
code does not produce: analysis.py stops at the array and visualize.py reduces it to one
mean per (noise, intensity), 130 rows. The last step is in plotting code that was not
released. claims.json froze the two readings before any of this ran:

  primary      mean of the 10 per-intensity means, sd across those 10 numbers
  alternative  mean and sd over all 1000 per-object values

Both are computed. The verdict follows the primary.
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
REF = os.path.join(ROOT, "data", "ref", "seg_sim_exported_data")


def published(metric, method="nellie"):
    name = ("IoU_" if metric == "iou" else "") + "Multigrid_F1_lv5_%s.txt" % method
    out = {}
    for line in io.open(os.path.join(REF, name), encoding="utf-8").read().splitlines()[1:]:
        p = line.split("\t")
        if len(p) >= 4:
            out[int(float(p[0]))] = (float(p[1]), float(p[2]), int(float(p[3])))
    return out


def aggregate(arr):
    per_intensity = [float(np.nanmean(arr[:, i, :])) for i in range(arr.shape[1])]
    return {
        "primary": {"mean": float(np.mean(per_intensity)), "sd": float(np.std(per_intensity)),
                    "n": len(per_intensity)},
        "alternative": {"mean": float(np.nanmean(arr)), "sd": float(np.nanstd(arr)),
                        "n": int(arr.size)},
        "per_intensity_means": per_intensity,
    }


noiseless = tifffile.imread(os.path.join(OUT, "noiseless", "no_noise.ome.tif"))
noiseless_label, n_objects = ndi.label(noiseless)
print("objetos no volume sem ruido:", n_objects)
assert n_objects == 1000, "gate congelado: o volume tem de ter 1000 componentes, tem %d" % n_objects

results = {"n_objects": int(n_objects), "levels": {}}
for std in LEVELS:
    # The ".ome" matters: without it, "gaussian_std_8" also matches "gaussian_std_8192"
    base = "gaussian_std_%d.ome" % std
    entry = {}
    sources = {
        "nellie": (os.path.join(OUT, "nellie_output", "nellie_necessities"), "skel_relabelled.ome.tif", True),
        "otsu": (os.path.join(OUT, "otsu"), ".tif", False),
        "triangle": (os.path.join(OUT, "triangle"), ".tif", False),
    }
    for method, (d, suffix, is_label) in sources.items():
        if not os.path.isdir(d):
            continue
        hits = [f for f in os.listdir(d) if base in f and f.endswith(suffix)]
        if not hits:
            entry[method] = {"erro": "sem saida"}
            continue
        im = tifffile.imread(os.path.join(d, sorted(hits)[0]))
        if im.ndim == 4:
            im = im[0]
        f1_arr, iou_arr = check_IoU(noiseless_label, im, is_label=is_label)
        entry[method] = {"f1": aggregate(f1_arr), "iou": aggregate(iou_arr)}
    results["levels"][str(std)] = entry

# compare nellie against the published table
pub_f1, pub_iou = published("f1"), published("iou")
lines = ["nivel  metrica  nosso (primaria)      publicado           delta   banda   passa"]
verdict_rows = []
for std in LEVELS:
    e = results["levels"].get(str(std), {}).get("nellie")
    if not e or "erro" in e:
        lines.append("%5d  sem saida do nellie" % std)
        continue
    for metric, pub in (("f1", pub_f1), ("iou", pub_iou)):
        ours = e[metric]["primary"]
        pm, ps, pn = pub[std]
        band = ps if ps > 0 else 0.01
        delta = ours["mean"] - pm
        ok = abs(delta) <= band
        verdict_rows.append(ok)
        lines.append("%5d  %-7s  %.4f +- %.4f   %.4f +- %.4f (N=%d)  %+.4f  %.4f  %s"
                      % (std, metric, ours["mean"], ours["sd"], pm, ps, pn, delta, band,
                         "ok" if ok else "FALHA"))
        alt = e[metric]["alternative"]
        lines.append("       %-7s  alternativa %.4f +- %.4f (N=%d)"
                     % ("", alt["mean"], alt["sd"], alt["n"]))

lines.append("")
lines.append("%d de %d medias dentro da banda" % (sum(verdict_rows), len(verdict_rows)))
txt = "\n".join(lines) + "\n"
io.open(os.path.join(ROOT, "runs", "logs", "analyse.log"), "w", encoding="utf-8", newline="\n").write(txt)
io.open(os.path.join(ROOT, "runs", "out", "results.json"), "w", encoding="utf-8", newline="\n").write(
    json.dumps(results, indent=1) + "\n")
print(txt)
