import json

ROOT = "/mnt/e/Ciencia/pipeline/2025-dauparas-ligandmpnn"
man = json.load(open(ROOT + "/data/structures/manifest.json"))

for flavour, missing in man["missing"].items():
    for pdb_id in missing:
        where = [s for s, ids in man["splits"].items() if pdb_id in ids]
        print(flavour, pdb_id, "belongs to", where)
