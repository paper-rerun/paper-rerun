# Which configs the A1 filter removes, and why (reference forces only)
import re
import sys
import numpy as np

key_value_re = re.compile(r'(\w+)=("([^"]*)"|(\S+))')
by_force = 0
by_sum = 0
both = 0
max_forces = []
with open(sys.argv[1]) as handle:
	while True:
		first_line = handle.readline()
		if not first_line:
			break
		number_of_atoms = int(first_line)
		header = handle.readline()
		info = {m.group(1): (m.group(3) if m.group(3) is not None else m.group(4)) for m in key_value_re.finditer(header)}
		rows = [handle.readline().split() for _ in range(number_of_atoms)]
		forces = np.array([[float(x) for x in row[4:7]] for row in rows])
		bLargeForce = (np.linalg.norm(forces, axis=1) > 15.0).any()
		bLargeSum = np.linalg.norm(forces.sum(axis=0)) > 0.1
		if bLargeForce or bLargeSum:
			by_force += int(bLargeForce and not bLargeSum)
			by_sum += int(bLargeSum and not bLargeForce)
			both += int(bLargeForce and bLargeSum)
			max_forces.append(np.linalg.norm(forces, axis=1).max())
			print(f"{info['config_type']}\tn={number_of_atoms}\tmax|F|={max_forces[-1]:.2f}\t|sumF|={np.linalg.norm(forces.sum(axis=0)):.3f}")
print(f"removed: only max|F|>15: {by_force}, only |sumF|>0.1: {by_sum}, both: {both}, total {by_force + by_sum + both}")
print(f"max|F| of removed configs: median {np.median(max_forces):.2f}, max {np.max(max_forces):.2f} eV/A")
