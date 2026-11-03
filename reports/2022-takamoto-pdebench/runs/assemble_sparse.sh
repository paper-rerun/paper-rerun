#!/bin/bash
# usage: assemble_sparse.sh <name.hdf5> -> data/sparse/<name.hdf5> at original size, zeros between head and tail (claims D14)
D=/mnt/e/Ciencia/noturno/2022-takamoto-pdebench/data/sparse
f=$D/$1; size=8232968312; TAIL=6264
[ -f "$f.head" ] && [ -f "$f.tail" ] || { echo "missing pieces for $1"; exit 1; }
rm -f "$f"; truncate -s $size "$f"
dd if="$f.head" of="$f" conv=notrunc bs=8M status=none
python3 - "$f" "$f.tail" $((size-TAIL)) <<'PY'
import sys
f,t,off=sys.argv[1],sys.argv[2],int(sys.argv[3])
b=open(t,'rb').read()
with open(f,'r+b') as o:
    o.seek(off); o.write(b)
    o.seek(off); assert o.read(len(b))==b
PY
ls -l "$f"
