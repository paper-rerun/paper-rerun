#!/bin/bash
# Released weights, straight from the authors' get_model_params.sh list.
set -euo pipefail

DEST=/mnt/e/Ciencia/pipeline/2025-dauparas-ligandmpnn/data/model_params
BASE=https://files.ipd.uw.edu/pub/ligandmpnn

mkdir -p "$DEST"

FILES="
proteinmpnn_v_48_002.pt
proteinmpnn_v_48_010.pt
proteinmpnn_v_48_020.pt
proteinmpnn_v_48_030.pt
ligandmpnn_v_32_005_25.pt
ligandmpnn_v_32_010_25.pt
ligandmpnn_v_32_020_25.pt
ligandmpnn_v_32_030_25.pt
per_residue_label_membrane_mpnn_v_48_020.pt
global_label_membrane_mpnn_v_48_020.pt
solublempnn_v_48_002.pt
solublempnn_v_48_010.pt
solublempnn_v_48_020.pt
solublempnn_v_48_030.pt
ligandmpnn_sc_v_32_002_16.pt
"

for f in $FILES; do
	if [ -s "$DEST/$f" ]; then
		echo "have $f"
		continue
	fi
	echo "get $f"
	wget -q --tries=3 --timeout=60 "$BASE/$f" -O "$DEST/$f" || { echo "FAILED $f"; rm -f "$DEST/$f"; }
done

echo "--- sha256 ---"
cd "$DEST" && sha256sum *.pt
ls -la "$DEST"
