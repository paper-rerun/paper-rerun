"""Read only the parameter-name dict at the head of each chain pickle.

Walks opcodes with pickletools.genops (which executes nothing) and collects the
unicode strings appearing before the first STACK_GLOBAL - those are the dict keys, in
column order. Reads ~7 kB per file instead of 2 GB.
"""
import glob, gzip, json, os, pickletools, sys

out = {}
for path in sorted(glob.glob(os.path.join(sys.argv[1], '*.pkl.gz'))):
    keys = []
    with gzip.open(path, 'rb') as f:
        for op, arg, pos in pickletools.genops(f):
            if op.name == 'STACK_GLOBAL':
                break
            if op.name in ('SHORT_BINUNICODE', 'BINUNICODE', 'UNICODE'):
                keys.append(arg)
    out[os.path.basename(path)] = keys

for name, keys in out.items():
    tail = [k for k in keys if 'red_noise' not in k]
    print('%-24s ncols=%3d  nonpulsar=%s' % (name, len(keys), tail))

json.dump(out, open(sys.argv[2], 'w'), indent=1)
