"""Recompute every number the report quotes, from runs/out/*.npz and data/ref."""
import io, os, json
import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REF = os.path.join(ROOT, "data", "ref", "seg_sim_exported_data")
LEVELS = [8, 1024, 8192, 32768]
out = []
P = out.append


def published(metric):
    name = "Multigrid_F1_lv5_nellie.txt" if metric == "f1" else "IoU_Multigrid_F1_lv5_nellie.txt"
    rows = {}
    for line in io.open(os.path.join(REF, name), encoding="utf-8").read().splitlines()[1:]:
        p = line.split("\t")
        rows[int(p[0])] = (float(p[1]), float(p[2]), int(p[3]))
    return rows


pub = {m: published(m) for m in ("f1", "iou")}
P("published rows (all 13 levels), F1 then IoU:")
for m in ("f1", "iou"):
    for k in sorted(pub[m]):
        P("  %-4s %6d  %.10f  %.10f  N=%d" % (m, k, *pub[m][k]))

G = {}
for std in LEVELS:
    for tag in ("", "_t0", "_t1"):
        f = os.path.join(ROOT, "runs", "out", "grid_%d%s.npz" % (std, tag))
        if os.path.exists(f):
            z = np.load(f)
            G[(std, tag)] = {"f1": z["f1"], "iou": z["iou"]}

P("")
P("A. grid_N.npz vs grid_N_t0.npz identical? (the report's main table and draw 0)")
for std in LEVELS:
    a, b = G[(std, "")], G[(std, "_t0")]
    P("  %6d  f1 %s  iou %s" % (std, np.array_equal(a["f1"], b["f1"]),
                                np.array_equal(a["iou"], b["iou"])))

P("")
P("B. report's verdict table recomputed (primary = mean of 10 means over axis 1)")
P("  level metric  mean      sd(ax1)   pub mean  pub sd   delta     band    pass")
for std in LEVELS:
    for m in ("f1", "iou"):
        arr = G[(std, "")][m]
        per = arr.mean(axis=(0, 2))
        mean, sd = per.mean(), per.std()
        pm, ps, _ = pub[m][std]
        band = ps if ps > 0 else 0.01
        d = mean - pm
        P("  %5d %-6s  %.4f    %.4f    %.4f    %.4f   %+.4f   %.4f  %s"
          % (std, m, mean, sd, pm, ps, d, band, "ok" if abs(d) <= band else "FAIL"))

P("")
P("C. aggregation scan, including candidates the report never tried")
cands = {}
for std in LEVELS:
    for m in ("f1", "iou"):
        arr = G[(std, "")][m]
        ps = pub[m][std][1]
        c = {
            "all 1000 cells (ddof0)": arr.std(),
            "all 1000 cells (ddof1)": arr.std(ddof=1),
            "sd of 10 means over ax0 (thickness)": arr.mean(axis=(1, 2)).std(),
            "sd of 10 means over ax1 (called intensity)": arr.mean(axis=(0, 2)).std(),
            "sd of 10 means over ax2 (called length)": arr.mean(axis=(0, 1)).std(),
            "mean of 10 within-slice sds, ax0": np.mean([arr[i].std() for i in range(10)]),
            "mean of 10 within-slice sds, ax1": np.mean([arr[:, i, :].std() for i in range(10)]),
            "mean of 10 within-slice sds, ax2": np.mean([arr[:, :, i].std() for i in range(10)]),
            "sem over 1000 cells": arr.std() / np.sqrt(1000),
            "sem of 10 means over ax1": arr.mean(axis=(0, 2)).std() / np.sqrt(10),
            "sd of 10 within-slice sds, ax1": np.std([arr[:, i, :].std() for i in range(10)]),
            "median-ish: sd of 100 cells in middle ax1 slice": arr[:, 4, :].std(),
        }
        for k, v in c.items():
            cands.setdefault(k, []).append((std, m, float(v), ps))
P("  mean |sd - pub sd| over the 8 pairs, and over the 6 pairs whose mean reproduces:")
six = [(1024, "f1"), (8192, "f1"), (8, "iou"), (1024, "iou"), (8192, "iou"), (32768, "iou")]
rank = []
for k, rows in cands.items():
    all8 = np.mean([abs(v - ps) for _, _, v, ps in rows])
    s6 = np.mean([abs(v - ps) for std, m, v, ps in rows if (std, m) in six])
    rank.append((all8, s6, k))
for all8, s6, k in sorted(rank):
    P("    %-45s  8 pairs %.4f   6 pairs %.4f" % (k, all8, s6))

P("")
P("D. per-pair comparison for the best few candidates")
for k in ("all 1000 cells (ddof0)", "mean of 10 within-slice sds, ax1",
          "mean of 10 within-slice sds, ax2", "sd of 10 means over ax2 (called length)"):
    P("  " + k)
    for std, m, v, ps in cands[k]:
        P("    %6d %-4s  ours %.4f   pub %.4f   diff %+.4f" % (std, m, v, ps, v - ps))

P("")
P("E. replicate spread, recomputed, with the n=2 confidence interval on sigma")
import math
# chi2 quantiles for 1 dof: 0.000982 (2.5%), 5.0239 (97.5%)
lo_mult, hi_mult = 1 / math.sqrt(5.0239), 1 / math.sqrt(0.000982)
P("  level metric  draw0    draw1    sd(ddof1)  pub sd   ratio   sd 95%% CI on sigma")
ratios = []
for m in ("f1", "iou"):
    for std in LEVELS:
        a = float(G[(std, "_t0")][m].mean())
        b = float(G[(std, "_t1")][m].mean())
        sd = float(np.std([a, b], ddof=1))
        ps = pub[m][std][1]
        r = ps / sd if sd > 0 else float("nan")
        if ps > 0 and sd > 0:
            ratios.append(r)
        P("  %5d %-6s  %.4f   %.4f   %.6f   %.4f   %7.1f  [%.5f, %.5f]"
          % (std, m, a, b, sd, ps, r, sd * lo_mult, sd * hi_mult))
P("  ratio range over the 7 pairs with pub sd > 0: %.1f to %.1f" % (min(ratios), max(ratios)))
P("  pairs where the 95%% upper bound on sigma still falls below the printed sd:")
for m in ("f1", "iou"):
    for std in LEVELS:
        a = float(G[(std, "_t0")][m].mean()); b = float(G[(std, "_t1")][m].mean())
        sd = float(np.std([a, b], ddof=1)); ps = pub[m][std][1]
        if ps > 0:
            P("    %5d %-4s upper %.4f vs printed %.4f -> %s"
              % (std, m, sd * hi_mult, ps, "below" if sd * hi_mult < ps else "NOT below"))

P("")
P("F. cells scoring both f1 == 0 and iou == 0, per level (report says 10, 0, 33, 58)")
for std in LEVELS:
    f1, iou = G[(std, "")]["f1"], G[(std, "")]["iou"]
    both = int(((f1 == 0) & (iou == 0)).sum())
    f0 = int((f1 == 0).sum())
    i0 = int((iou == 0).sum())
    sub = int(((f1 == 0) & (iou > 0)).sum())
    P("  %6d  f1==0 %4d  iou==0 %4d  both %4d  f1==0 & 0<iou %4d" % (std, f0, i0, both, sub))

P("")
P("G. sigma=8 F1: how many of 1000 cells fail (report says 22)")
for tag in ("_t0", "_t1"):
    f1 = G[(8, tag)]["f1"]
    P("  draw %s: cells with f1 < 1: %d ; mean %.4f" % (tag, int((f1 < 1).sum()), f1.mean()))

io.open(os.path.join(ROOT, "review", "01_arith.log"), "w", encoding="utf-8", newline="\n").write(
    "\n".join(out) + "\n")
