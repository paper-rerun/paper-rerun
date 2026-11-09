# Print only markdown and code sources of a notebook, never its outputs
import json, sys
nb = json.load(open(sys.argv[1], encoding="utf-8"))
for i, c in enumerate(nb["cells"]):
    print(f"--- [{i}] {c['cell_type']}")
    print("".join(c["source"]))
