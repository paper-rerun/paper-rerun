# Independent Fig. 4 readout: colored bars + stroked y ticks, journal PDF p.7
import fitz, sys
page = fitz.open(sys.argv[1])[6]
bars, ticks = [], []
for d in page.get_drawings():
    r = d["rect"]
    if not (530 < r.y1 < 680): continue
    f = d.get("fill")
    if f and f != (0.0, 0.0, 0.0) and r.y1 > 672 and r.height > 0.1 and r.width > 3:
        bars.append((r.x0, r.y0, r.y1, tuple(round(c, 3) for c in f)))
    if d.get("color") and f is None:
        for it in d["items"]:
            if it[0] == "l" and abs(it[1].y - it[2].y) < 1e-3 and abs(it[1].x - it[2].x) < 6:
                ticks.append((round(min(it[1].x, it[2].x), 3), round(it[1].y, 4)))
print("ticks", sorted(set(ticks)))
for b in sorted(bars): print([round(b[0], 3), round(b[1], 4), round(b[2], 4), b[3]])
