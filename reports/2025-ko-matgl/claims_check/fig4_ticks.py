# Find y-axis tick marks left of the axis frames (x ~128.65 and ~347.6)
import fitz, sys
page = fitz.open(sys.argv[1])[6]
for d in page.get_drawings():
    r = d["rect"]
    for ax in (128.651, 347.616):
        if abs(r.x1 - ax) < 0.05 and r.width < 3 and 540 < r.y0 < 680:
            print(ax, round(r.x0, 3), round(r.y0, 4), round(r.y1, 4), d.get("fill"), d.get("color"), d["type"])
pix = page.get_pixmap(clip=fitz.Rect(80, 540, 520, 705), dpi=300); pix.save(sys.argv[2])
