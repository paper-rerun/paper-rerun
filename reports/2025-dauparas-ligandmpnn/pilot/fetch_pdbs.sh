#!/bin/bash
# Download PDB biological assembly 1 for every id in the three test splits.
# Paper trains/tests on "PDB biounits", so assembly 1 is the right file, not the asymmetric unit.
set -u
ROOT=/mnt/e/Ciencia/artigos/2025-dauparas-ligandmpnn
OUT=$ROOT/pdbs
mkdir -p "$OUT"

fetch_one() {
	id=$1
	out=$2/${id}.pdb
	if [ -s "$out" ]; then
		return 0
	fi
	# Assembly 1; falls back to the plain entry when no assembly file exists
	if wget -q "https://files.rcsb.org/download/${id}.pdb1.gz" -O "$out.gz" && [ -s "$out.gz" ]; then
		gunzip -f "$out.gz"
		return 0
	fi
	rm -f "$out.gz"
	if wget -q "https://files.rcsb.org/download/${id}.pdb" -O "$out" && [ -s "$out" ]; then
		echo "$id: no assembly file, used asymmetric unit" >&2
		return 0
	fi
	rm -f "$out"
	echo "$id: FAILED" >&2
	return 1
}
export -f fetch_one

cd "$ROOT/repo/training"
python3 -c "
import json
ids = []
for f in ['test_small_molecule.json','test_nucleotide.json','test_metal.json']:
    ids += json.load(open(f))
print('\n'.join(ids))
" > "$OUT/all_ids.txt"

wc -l < "$OUT/all_ids.txt"
xargs -a "$OUT/all_ids.txt" -P 8 -I{} bash -c 'fetch_one "$@"' _ {} "$OUT"
echo "downloaded: $(ls -1 "$OUT"/*.pdb | wc -l)"
