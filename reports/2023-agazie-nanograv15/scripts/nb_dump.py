# Dump code/markdown cells (and short text outputs) of a notebook, for reading
import json, sys
nb = json.load(open(sys.argv[1], encoding='utf-8'))
for i, c in enumerate(nb['cells']):
    src = ''.join(c.get('source', ''))
    print(f'--- [{i}] {c["cell_type"]}')
    print(src)
    for o in c.get('outputs', []):
        t = o.get('text') or o.get('data', {}).get('text/plain')
        if t:
            t = ''.join(t)
            print('>>> ' + t[:600])
