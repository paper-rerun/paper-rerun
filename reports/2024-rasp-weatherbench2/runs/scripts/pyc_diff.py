# Compare the 21:42 bytecode cache of wb2_rmse.py with the current source, function by function
import dis
import marshal
import sys

ROOT = '/mnt/e/Ciencia/noturno/2024-rasp-weatherbench2/runs/scripts/'
with open(ROOT + '__pycache__/wb2_rmse.cpython-311.pyc', 'rb') as pyc_file:
	pyc_file.read(16)
	old_module = marshal.load(pyc_file)
new_module = compile(open(ROOT + 'wb2_rmse.py').read(), ROOT + 'wb2_rmse.py', 'exec')


def functions(code, prefix=''):
	found = {}
	for const in code.co_consts:
		if hasattr(const, 'co_code'):
			name = prefix + const.co_name
			found[name] = const
			found.update(functions(const, name + '.'))
	return found


def listing(code):
	return [(ins.opname, repr(ins.argval)) for ins in dis.get_instructions(code)]


old_functions, new_functions = functions(old_module), functions(new_module)
print('module-level identical:', listing(old_module) == listing(new_module))
for name in sorted(set(old_functions) | set(new_functions)):
	if name not in old_functions or name not in new_functions:
		print(name, 'only in', 'new' if name in new_functions else 'old')
		continue
	if listing(old_functions[name]) != listing(new_functions[name]):
		print('DIFFERS:', name)
		old_lines = listing(old_functions[name])
		new_lines = listing(new_functions[name])
		import difflib
		for line in difflib.unified_diff([' '.join(x) for x in old_lines], [' '.join(x) for x in new_lines], lineterm='', n=2):
			print('   ', line)
