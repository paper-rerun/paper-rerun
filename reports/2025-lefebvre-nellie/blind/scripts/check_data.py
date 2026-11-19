"""Checks C1-C5 against the published Source Data rows, plus an N-consistency test.

Run: python -I check_data.py <dir with the extracted .txt files> <out.txt>
"""
import os
import sys
import io
import math
import numpy as np

OUT = io.StringIO()


def say(*a):
    print(*a, file=OUT)


def parse(path):
    rows = []
    with open(path, encoding="utf-8-sig") as f:
        header = f.readline().rstrip("\n").split("\t")
        for line in f:
            line = line.rstrip("\n")
            if not line.strip():
                continue
            rows.append(line.split("\t"))
    return header, rows


def sd_max(n, m, ddof=0):
    """Largest possible sd of n values in [0,1] with mean m.

    Extremal configuration: k values at 1, one at the remainder, rest at 0.
    """
    total = n * m
    k = int(math.floor(total + 1e-12))
    rem = total - k
    sq = k * 1.0 + rem * rem
    var = sq / n - m * m
    if ddof:
        var = var * n / (n - ddof)
    return math.sqrt(max(var, 0.0))


F1_GRID = [0.0] + [2.0 / (2.0 + k) for k in range(0, 400)]


def explain_with_n(m, s, n, tol=5e-10):
    """Try to find a multiset of n values from the F1 grid with this mean and population sd."""
    target_sum = m * n
    target_sq = (s * s + m * m) * n
    for n1 in range(n, -1, -1):          # how many sections scored exactly 1.0
        S = target_sum - n1
        Q = target_sq - n1
        r = n - n1
        if S < -1e-9 or Q < -1e-9 or r < 0:
            continue
        if S <= 1e-9 and Q <= 1e-9:
            if r >= 0:
                return (n1, [])
        # one extra non-zero value v with multiplicity c, rest zeros
        for c in range(1, r + 1):
            v = S / c
            if v <= 0 or v > 1:
                continue
            if abs(c * v * v - Q) < tol:
                for g in F1_GRID:
                    if abs(g - v) < 1e-9:
                        return (n1, [(c, v)])
        # two extra non-zero values, each from the grid
        for g1 in F1_GRID[1:60]:
            for c1 in range(1, min(r, 6) + 1):
                S2 = S - c1 * g1
                Q2 = Q - c1 * g1 * g1
                if S2 < -1e-9 or Q2 < -1e-9:
                    continue
                for c2 in range(1, min(r - c1, 6) + 1):
                    v = S2 / c2
                    if v <= 0 or v > 1:
                        continue
                    if abs(c2 * v * v - Q2) < tol:
                        for g in F1_GRID:
                            if abs(g - v) < 1e-9:
                                return (n1, [(c1, g1), (c2, g)])
    return None


def main():
    d, out_path = sys.argv[1:3]
    expected_noise = [8, 16, 32, 64, 128, 256, 512, 1024, 2048, 4096, 8192, 16384, 32768]

    f1_path = os.path.join(d, "Multigrid_F1_lv5_nellie.txt")
    iou_path = os.path.join(d, "IoU_Multigrid_F1_lv5_nellie.txt")

    tables = {}
    for tag, p in (("F1", f1_path), ("IoU", iou_path)):
        header, rows = parse(p)
        tables[tag] = (header, rows)
        say(f"--- {os.path.basename(p)} ---")
        say(f"header: {header}")
        say(f"rows:   {len(rows)}, columns per row: {sorted({len(r) for r in rows})}")
        noise = [int(r[0]) for r in rows]
        say(f"C1 noise column == expected 13 levels: {noise == expected_noise}  ({noise})")
        Ns = sorted({r[3] for r in rows})
        say(f"C2 N column distinct values: {Ns}")
        say("")

    say("C3 F1/IoU row alignment:")
    hf, rf = tables["F1"]
    hi, ri = tables["IoU"]
    say(f"  same row count: {len(rf) == len(ri)}")
    say(f"  same noise order: {[r[0] for r in rf] == [r[0] for r in ri]}")
    say(f"  same N column: {[r[3] for r in rf] == [r[3] for r in ri]}")
    say("")

    for tag in ("F1", "IoU"):
        header, rows = tables[tag]
        say(f"=== {tag}: C4 / C5 / N-consistency ===")
        say(f"{'noise':>7} {'mean':>13} {'sd':>13} {'N':>4} "
            f"{'sdmax(N=10)':>12} {'sdmax(N=100)':>13} {'verdict':>28}")
        for r in rows:
            noise = int(r[0])
            m = float(r[1])
            s = float(r[2])
            n = int(r[3])
            m_ok = -1e-12 <= m <= 1 + 1e-12
            s10 = sd_max(10, m)
            s100 = sd_max(100, m)
            s10d1 = sd_max(10, m, ddof=1)
            s100d1 = sd_max(100, m, ddof=1)
            verdict = []
            if not m_ok:
                verdict.append("mean out of [0,1]")
            if s > s10 + 1e-9 and s > s10d1 + 1e-9:
                verdict.append("N=10 IMPOSSIBLE")
            if s > s100 + 1e-9 and s > s100d1 + 1e-9:
                verdict.append("N=100 impossible too")
            if abs(m) < 1e-12 and abs(s) > 1e-12:
                verdict.append("C5 violated (mean 0, sd>0)")
            if abs(s) < 1e-12 and not (abs(m) < 1e-12 or abs(m - 1) < 1e-12):
                verdict.append("C5 violated (sd 0, mean not 0/1)")
            say(f"{noise:>7} {m:>13.10f} {s:>13.10f} {n:>4} {s10:>12.6f} {s100:>13.6f} "
                f"{(', '.join(verdict) if verdict else 'ok'):>28}")
        say("")

    say("=== Which N reproduces the published (mean, sd) pair exactly? ===")
    say("For each F1 row, search for a multiset of N section scores drawn from the")
    say("F1 values the released code can emit, {0} U {2/(2+fp)}, matching mean and")
    say("population sd to 5e-10.")
    header, rows = tables["F1"]
    for r in rows:
        m, s, n = float(r[1]), float(r[2]), int(r[3])
        line = f"noise {int(r[0]):>6}: mean {m:.10f} sd {s:.10f} (published N={n})"
        found = []
        for trial_n in (10, 100, 1000):
            res = explain_with_n(m, s, trial_n)
            if res is not None:
                n1, extras = res
                desc = f"{n1} x 1.0" + "".join(f" + {c} x {v:.10f}" for c, v in extras)
                zeros = trial_n - n1 - sum(c for c, _ in extras)
                if zeros:
                    desc += f" + {zeros} x 0.0"
                found.append(f"N={trial_n}: {desc}")
        say(line)
        if found:
            for f in found:
                say(f"    {f}")
        else:
            say("    no exact decomposition found at N in (10, 100, 1000)")
    say("")

    say("=== IoU rows: same question, continuous values so only the N bound applies ===")
    header, rows = tables["IoU"]
    for r in rows:
        m, s, n = float(r[1]), float(r[2]), int(r[3])
        say(f"noise {int(r[0]):>6}: mean {m:.10f} sd {s:.10f} N={n} | "
            f"sd/sdmax(10)={s/max(sd_max(10,m),1e-12):7.3f} "
            f"sd/sdmax(100)={s/max(sd_max(100,m),1e-12):7.3f}")
    say("")

    say("=== other methods, N column and the same N=10 feasibility test (F1 files) ===")
    for fn in sorted(os.listdir(d)):
        if not fn.startswith("Multigrid_F1_lv5_"):
            continue
        header, rows = parse(os.path.join(d, fn))
        bad10 = 0
        bad100 = 0
        for r in rows:
            m, s = float(r[1]), float(r[2])
            if s > sd_max(10, m, ddof=1) + 1e-9:
                bad10 += 1
            if s > sd_max(100, m, ddof=1) + 1e-9:
                bad100 += 1
        say(f"{fn:<40} N={rows[0][3]:>4} rows={len(rows):>3} "
            f"rows where N=10 is impossible: {bad10:>3}  where N=100 is impossible: {bad100:>3}")

    open(out_path, "w", encoding="utf-8").write(OUT.getvalue())


if __name__ == "__main__":
    main()
