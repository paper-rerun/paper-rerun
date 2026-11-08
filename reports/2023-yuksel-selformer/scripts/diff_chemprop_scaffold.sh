#!/bin/bash
# The repo pinned chemprop 1.4.1 at publication time and 1.5.2 later. Does the scaffold
# split itself differ between the two? Diff the file that decides it, taken from the sdists.
set -u
B=/mnt/e/Ciencia/noturno/2023-yuksel-selformer
W=$B/dl/chemprop_src
mkdir -p "$W"
cd "$W"
for v in 1.4.1 1.5.2; do
	url=$(curl -s "https://pypi.org/pypi/chemprop/${v}/json" | python3 -I -c "
import json,sys
d=json.load(sys.stdin)
for f in d['urls']:
    if f['filename'].endswith('.tar.gz'):
        print(f['url']); break
")
	echo "$v -> $url"
	curl -sL "$url" -o "chemprop-${v}.tar.gz"
	rm -rf "x${v}"
	mkdir -p "x${v}"
	tar -xzf "chemprop-${v}.tar.gz" -C "x${v}" "chemprop-${v}/chemprop/data/scaffold.py"
done
echo "=== diff of chemprop/data/scaffold.py, 1.4.1 vs 1.5.2 ==="
if diff -u x1.4.1/chemprop-1.4.1/chemprop/data/scaffold.py x1.5.2/chemprop-1.5.2/chemprop/data/scaffold.py; then
	echo "IDENTICAL"
fi
echo "=== scaffold_split signature in 1.5.2 ==="
sed -n '/def scaffold_split/,/^def /p' x1.5.2/chemprop-1.5.2/chemprop/data/scaffold.py | head -60
