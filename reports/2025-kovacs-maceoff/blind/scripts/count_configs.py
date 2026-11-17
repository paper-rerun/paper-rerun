# Count configurations and atoms per config_type in the released test xyz, stdlib only
import re
import sys
from collections import Counter

path = sys.argv[1]
config_counts = Counter()
atom_counts = Counter()
size_range = {}
header_re = re.compile(r'config_type=("([^"]*)"|(\S+))')
with open(path, "r") as handle:
	while True:
		first_line = handle.readline()
		if not first_line:
			break
		number_of_atoms = int(first_line.strip())
		header = handle.readline()
		match = header_re.search(header)
		config_type = match.group(2) if match.group(2) is not None else match.group(3)
		config_counts[config_type] += 1
		atom_counts[config_type] += number_of_atoms
		low, high = size_range.get(config_type, (10 ** 9, 0))
		size_range[config_type] = (min(low, number_of_atoms), max(high, number_of_atoms))
		for _ in range(number_of_atoms):
			handle.readline()

total = 0
for config_type in sorted(config_counts):
	low, high = size_range[config_type]
	print(f"{config_type}\tconfigs={config_counts[config_type]}\tatoms={atom_counts[config_type]}\tsize={low}-{high}")
	total += config_counts[config_type]
print(f"TOTAL\tconfigs={total}")
