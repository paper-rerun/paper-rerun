"""Checks the authors' own read_chains_y3a2.py against every chain in the same folder.

Their script takes sigma_8 from column index 30 and the weight from index 36, with a comment
saying so. Those indices are only right for a file whose header has exactly 37 columns. This
fetches the header line of every chain and reports what sits at 30 and 36 in each.

Usage: 04_header_audit.py <out.json>
"""
import json
import subprocess
import sys

OUT = sys.argv[1]
BASE = "https://desdr-server.ncsa.illinois.edu/despublic/y3a2_files/chains"
LIST = subprocess.run(["curl", "-s", "-A", "paper-rerun/1.0", "-m", "60", BASE + "/"],
	capture_output=True, text=True).stdout
files = sorted({f for f in __import__("re").findall(r'href="([^"]+\.txt)"', LIST)})

out = {"files": {}, "n_files": len(files), "wrong_sigma8": [], "wrong_weight": []}
for f in files:
	# Only the first few KB: the header is the first line
	head = subprocess.run(["curl", "-s", "-A", "paper-rerun/1.0", "-m", "90", "-r", "0-8000",
		"%s/%s" % (BASE, f)], capture_output=True, text=True).stdout
	line = head.split("\n", 1)[0].lstrip("#").rstrip()
	names = [n.strip().lower() for n in line.split("\t")]
	at30 = names[30] if len(names) > 30 else None
	at36 = names[36] if len(names) > 36 else None
	out["files"][f] = {"n_columns": len(names), "index_30": at30, "index_36": at36}
	if at30 != "cosmological_parameters--sigma_8":
		out["wrong_sigma8"].append(f)
	if at36 != "weight":
		out["wrong_weight"].append(f)

out["n_wrong_sigma8"] = len(out["wrong_sigma8"])
out["n_wrong_weight"] = len(out["wrong_weight"])
open(OUT, "w", encoding="utf-8", newline="\n").write(json.dumps(out, indent=1))
print(json.dumps({k: v for k, v in out.items() if k != "files"}, indent=1))
