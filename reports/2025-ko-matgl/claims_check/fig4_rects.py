# Independent readout of Fig. 4 bars: list filled rectangles and text on journal PDF p.7
import fitz, sys, json
doc = fitz.open(sys.argv[1]); page = doc[6]
rects = []
for d in page.get_drawings():
    if d.get("fill") is None: continue
    r = d["rect"]
    if r.width < 30 and r.height > 0.3 and r.y1 > 500 and r.y1 < 700:
        rects.append((round(r.x0,3), round(r.y0,4), round(r.x1,3), round(r.y1,4), tuple(round(c,3) for c in d["fill"])))
rects.sort()
for x in rects: print(x)
print("N", len(rects))
for b in page.get_text("dict")["blocks"]:
    for l in b.get("lines", []):
        for s in l["spans"]:
            bb = s["bbox"]
            if 480 < bb[1] < 720: print("T", [round(v,2) for v in bb], repr(s["text"]))
