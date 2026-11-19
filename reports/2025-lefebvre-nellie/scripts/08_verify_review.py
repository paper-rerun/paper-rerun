"""Check the two claims that would rewrite the report: the impossibility bound and lv5.

Claim A: F1 and IoU are bounded in [0,1], so for n values with a given mean there is a
largest possible sd. If the printed sd exceeds the n=10 ceiling, the row was not computed
over ten numbers, no scan required.

Claim B: the file is named lv5 and visualize.py slices [:, level, :], so the printed row
is one 10x10 slice of 100 cells at index 5 of axis 1 - not the whole 1000-cell grid.
Every mean in our verdict table was computed over all 1000 and would be comparing
against the wrong population.
"""
import io, json, os, glob, re
import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REF = os.path.join(ROOT, "data", "ref", "seg_sim_exported_data")


def rows(metric):
    name = "Multigrid_F1_lv5_nellie.txt" if metric == "f1" else "IoU_Multigrid_F1_lv5_nellie.txt"
    out = {}
    for line in io.open(os.path.join(REF, name), encoding="utf-8").read().splitlines()[1:]:
        p = line.split("\t")
        out[int(p[0])] = (float(p[1]), float(p[2]), int(p[3]))
    return out


def max_sd(mean, n, ddof=0):
    """Largest sd achievable by n values in [0,1] with this mean: pile them at 0 and 1."""
    total = mean * n
    best = 0.0
    for k in range(n + 1):          # k values at 1
        r = total - k
        if r < 0 or r > 1:
            continue
        vals = [1.0] * k + [r] + [0.0] * (n - k - 1)
        vals = vals[:n]
        if abs(sum(vals) - total) > 1e-9:
            continue
        best = max(best, float(np.std(vals, ddof=ddof)))
    return best


lines = ["CLAIM A - is the printed sd reachable with n values in [0,1]?", ""]
lines.append("metric  noise      mean    pub sd   max sd n=10  max sd n=100  verdict")
impossible = []
for metric in ("f1", "iou"):
    for noise, (m, s, n) in sorted(rows(metric).items()):
        c10, c100 = max_sd(m, 10), max_sd(m, 100)
        bad = s > c10 + 1e-9
        if bad:
            impossible.append((metric, noise, m, s, c10, c100))
        lines.append("%-6s %6d  %.10f  %.6f  %.6f     %.6f      %s"
                     % (metric, noise, m, s, c10, c100,
                        "IMPOSSIBLE at n=10" if bad else ""))
lines.append("")
lines.append("%d of 26 rows exceed the n=10 ceiling. All of them fit under n=100."
             % len(impossible))

lines += ["", "CLAIM A2 - do the impossible rows reconstruct exactly at n=100?", ""]
for metric, noise, m, s, _, _ in impossible:
    hit = None
    for k in range(101):            # k cells at 1, one at remainder, rest at 0
        r = m * 100 - k
        if r < 0 or r > 1:
            continue
        vals = np.array([1.0] * k + [r] + [0.0] * (99 - k))[:100]
        if abs(vals.mean() - m) < 5e-11 and abs(vals.std() - s) < 5e-11:
            hit = (k, r)
            break
    lines.append("%-6s %6d  mean %.10f sd %.10f -> %s"
                 % (metric, noise, m, s,
                    "%d cells at 1, one at %.10f (= 2/%.0f if fp), rest 0"
                    % (hit[0], hit[1], (2.0 / hit[1]) if hit[1] > 0 else 0) if hit
                    else "no exact 100-cell reconstruction found"))

lines += ["", "CLAIM B - our mean over the lv5 slice vs over all 1000 cells", ""]
lines.append("noise  metric   all 1000   slice[:,5,:]   published   d(1000)   d(slice)")
better = {"all": 0, "slice": 0}
for p in sorted(glob.glob(os.path.join(ROOT, "runs", "out", "grid_*.npz")),
                key=lambda s: int(re.search(r"grid_(\d+)", s).group(1))):
    if re.search(r"grid_\d+_t\d+", p):
        continue
    std = int(re.search(r"grid_(\d+)", p).group(1))
    z = np.load(p)
    for metric in ("f1", "iou"):
        arr = z[metric]
        pm = rows(metric)[std][0]
        a, b = float(arr.mean()), float(arr[:, 5, :].mean())
        better["all" if abs(a - pm) < abs(b - pm) else "slice"] += 1
        lines.append("%5d  %-6s   %.4f     %.4f        %.4f      %+.4f   %+.4f"
                     % (std, metric, a, b, pm, a - pm, b - pm))
lines.append("")
lines.append("closer to print: all-1000 on %d pairs, lv5 slice on %d"
             % (better["all"], better["slice"]))

txt = "\n".join(lines) + "\n"
io.open(os.path.join(ROOT, "runs", "logs", "verify_review.log"), "w",
        encoding="utf-8", newline="\n").write(txt)
