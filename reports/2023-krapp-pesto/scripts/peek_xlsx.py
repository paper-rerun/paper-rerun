# Read an xlsx with zipfile only (openpyxl drops every sheet of this file as "invalid specification")
# Usage: python peek_xlsx.py <xlsx> <sheet name or ""> <out csv or "">
import re
import sys
import zipfile

path, want, out = sys.argv[1], sys.argv[2], sys.argv[3]
z = zipfile.ZipFile(path)
wb = z.read("xl/workbook.xml").decode("utf8")
rels = z.read("xl/_rels/workbook.xml.rels").decode("utf8")
rel_target = dict(re.findall(r'Id="([^"]+)"[^>]*Target="([^"]+)"', rels))
rel_target.update({a: b for b, a in re.findall(r'Target="([^"]+)"[^>]*Id="([^"]+)"', rels)})
sheets = re.findall(r'<sheet [^>]*name="([^"]+)"[^>]*r:id="([^"]+)"', wb)
shared = []
if "xl/sharedStrings.xml" in z.namelist():
	ss = z.read("xl/sharedStrings.xml").decode("utf8")
	for si in re.findall(r"<si>(.*?)</si>", ss, re.S):
		shared.append("".join(re.findall(r"<t[^>]*>(.*?)</t>", si, re.S)))
for name, rid in sheets:
	target = rel_target[rid].lstrip("/")
	if not target.startswith("xl/"):
		target = "xl/" + target
	xml = z.read(target).decode("utf8")
	rows = []
	for row in re.findall(r"<row[^>]*>(.*?)</row>", xml, re.S):
		cells = {}
		for ref, attrs, body in re.findall(r'<c r="([A-Z]+)\d+"([^>]*?)(?:/>|>(.*?)</c>)', row, re.S):
			v = re.search(r"<v>(.*?)</v>", body or "")
			val = v.group(1) if v else "".join(re.findall(r"<t[^>]*>(.*?)</t>", body or ""))
			if 't="s"' in attrs and v:
				val = shared[int(val)]
			cells[ref] = val
		rows.append(cells)
	print("SHEET", name, len(rows))
	if want and name == want:
		cols = sorted({c for r in rows for c in r}, key=lambda c: (len(c), c))
		with open(out, "w") as fs:
			for r in rows:
				fs.write(",".join(r.get(c, "") for c in cols) + "\n")
	elif not want:
		for r in rows[:4]:
			print("   ", list(r.items())[:10])
