"""Counts malformed lines in the deposit's TSV before anything is computed from it."""
import collections
import lzma
import sys

n = 0
widths = collections.Counter()
examples = {}
with lzma.open(sys.argv[1], "rt", encoding="utf-8") as fh:
	header = fh.readline().rstrip("\n").split("\t")
	for line in fh:
		f = line.rstrip("\n").split("\t")
		n += 1
		widths[len(f)] += 1
		if len(f) != len(header) and len(f) not in examples:
			examples[len(f)] = (n, line[:300])
out = ["header %d columns, %d data lines" % (len(header), n)]
for w, c in sorted(widths.items()):
	out.append("  %d columns: %d lines" % (w, c))
for w, (ln, text) in sorted(examples.items()):
	out.append("first odd line with %d columns, line %d: %r" % (w, ln, text))
open(sys.argv[2], "w", encoding="utf-8", newline="\n").write("\n".join(out))
print("\n".join(out))
