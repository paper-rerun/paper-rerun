import gzip, pickletools, sys

path = sys.argv[1]
ops = []
with gzip.open(path, 'rb') as f:
    for op, arg, pos in pickletools.genops(f):
        if isinstance(arg, (bytes, bytearray)) and len(arg) > 40:
            arg = '<%d bytes>' % len(arg)
        if isinstance(arg, str) and len(arg) > 60:
            arg = arg[:60] + '...'
        ops.append((pos, op.name, arg))
print('total ops:', len(ops))
print('--- last 80 ---')
for pos, name, arg in ops[-80:]:
    print('%10d %-18s %r' % (pos, name, arg))
print('--- all GLOBAL-ish ---')
for pos, name, arg in ops:
    if name in ('GLOBAL', 'STACK_GLOBAL', 'INST', 'NEWOBJ', 'NEWOBJ_EX'):
        print(pos, name, arg)
print('--- unicode strings after op 900 ---')
seen = []
for pos, name, arg in ops[900:]:
    if name.endswith('BINUNICODE') or name == 'UNICODE':
        seen.append(arg)
print(seen[:60], '... n=', len(seen))
