"""List the global names a pickle REFERS to, without executing any of them.

pickletools.genops only walks opcodes; it never imports or calls anything.
"""
import gzip, pickletools, sys
from collections import Counter

path = sys.argv[1]
limit = int(sys.argv[2]) if len(sys.argv) > 2 else 400000

globals_seen = Counter()
head = []
n = 0
with gzip.open(path, 'rb') as f:
    for op, arg, pos in pickletools.genops(f):
        n += 1
        if op.name in ('GLOBAL', 'STACK_GLOBAL', 'INST', 'OBJ', 'NEWOBJ', 'NEWOBJ_EX', 'REDUCE', 'BUILD'):
            globals_seen[(op.name, str(arg))] += 1
        if n <= 120:
            head.append('%6d %-16s %r' % (pos, op.name, arg if not isinstance(arg, (bytes, bytearray)) or len(arg) < 60 else arg[:60]))
        if n >= limit:
            print('... stopped after %d opcodes' % n)
            break

print('\n'.join(head))
print('--- global/reduce ops ---')
for k, v in globals_seen.most_common(60):
    print(v, k)
print('total opcodes walked:', n)
