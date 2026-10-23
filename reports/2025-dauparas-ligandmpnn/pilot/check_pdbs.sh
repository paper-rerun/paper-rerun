#!/bin/bash
P=/mnt/e/Ciencia/artigos/2025-dauparas-ligandmpnn/pdbs
for i in $(cat "$P/all_ids.txt"); do
	if [ ! -s "$P/$i.pdb" ]; then
		echo "MISSING $i"
	fi
done
echo "have: $(ls -1 "$P"/*.pdb | wc -l)"
