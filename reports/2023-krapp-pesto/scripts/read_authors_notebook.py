# Dump the saved outputs of the authors' interface_ppi_benchmark.ipynb (commit ba651aa) to plain files
# Usage: python -I read_authors_notebook.py <repo_dir> <out_dir>
import json
import re
import sys

repo_dir, out_dir = sys.argv[1], sys.argv[2]
nb = json.load(open(repo_dir + "/interface_ppi_benchmark.ipynb", encoding="utf8"))

# Cell 6: one line per dataset item, "KEY, acc=..., auc=..., std=..."
cell6 = "".join("".join(o.get("text", [])) for o in nb["cells"][6]["outputs"])
rows = []
for line in cell6.splitlines():
	m = re.match(r"^(\S+/\S+/\d+/\S+), .*auc=([0-9.]+|nan)", line)
	if m:
		rows.append((m.group(1), m.group(2)))
with open(out_dir + "/authors_cell6_pesto_auc_per_item.csv", "w") as fs:
	fs.write("key,auc\n")
	for key, auc in rows:
		fs.write(f"{key},{auc}\n")
print("cell 6 items:", len(rows))

# Cell 9: the per-structure table (text/plain of the displayed DataFrame)
for o in nb["cells"][9]["outputs"]:
	data = o.get("data", {})
	if "text/plain" in data:
		text = "".join(data["text/plain"])
		open(out_dir + "/authors_cell9_table.txt", "w").write(text)
		print("cell 9 table lines:", len(text.splitlines()))
	if "text/html" in data:
		html = "".join(data["text/html"])
		open(out_dir + "/authors_cell9_table.html", "w").write(html)
		trs = re.findall(r"<tr>(.*?)</tr>", html, re.S)
		with open(out_dir + "/authors_cell9_table.csv", "w") as fs:
			fs.write("row,sid,PeSTo,MaSIF-site,SPPIDER,PSIVER,ScanNet,best\n")
			n = 0
			for tr in trs:
				cells = [re.sub(r"<[^>]+>", "", c).strip() for c in re.findall(r"<t[hd][^>]*>(.*?)</t[hd]>", tr, re.S)]
				if len(cells) == 8 and cells[1] != "sid":
					fs.write(",".join(cells) + "\n")
					n += 1
		print("cell 9 html rows:", n)

# Cell 7: summary line
print("cell 7:", "".join("".join(o.get("text", [])) for o in nb["cells"][7]["outputs"] if o.get("name") == "stdout"))
