import json

BASE = "/mnt/e/Ciencia/pipeline/2025-dauparas-ligandmpnn/repo/training/"

for name in ("test_small_molecule.json", "test_nucleotide.json", "test_metal.json"):
    data = json.load(open(BASE + name))
    head = data[:4] if isinstance(data, list) else list(data)[:4]
    print(name, type(data).__name__, len(data), head)
