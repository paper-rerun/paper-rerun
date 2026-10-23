import json
import os

BASE = "/mnt/e/Ciencia/pipeline/2025-dauparas-ligandmpnn/exec/B1-small-molecule-split"
man = json.load(open(os.path.join(BASE, "inputs_manifest.json")))
paths = {r["input"]: "" for r in man["records"]}
json.dump(paths, open(os.path.join(BASE, "pdb_list.json"), "w"), indent=0)
json.dump(dict(list(paths.items())[:3]), open(os.path.join(BASE, "pdb_list_smoke.json"), "w"), indent=0)
print(len(paths))
