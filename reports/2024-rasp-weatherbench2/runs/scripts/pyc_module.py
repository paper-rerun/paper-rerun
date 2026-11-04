import dis, marshal, difflib
ROOT = '/mnt/e/Ciencia/noturno/2024-rasp-weatherbench2/runs/scripts/'
f = open(ROOT + '__pycache__/wb2_rmse.cpython-311.pyc', 'rb'); f.read(16); old = marshal.load(f)
new = compile(open(ROOT + 'wb2_rmse.py').read(), 'x', 'exec')
L = lambda c: [i.opname + ' ' + repr(i.argval) for i in dis.get_instructions(c) if 'code object' not in repr(i.argval)]
for l in difflib.unified_diff(L(old), L(new), lineterm='', n=1): print(l)
