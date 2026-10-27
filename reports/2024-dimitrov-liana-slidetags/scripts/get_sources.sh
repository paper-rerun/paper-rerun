#!/bin/bash
# Download SI, peer review file and Source Data Fig. 4 into sources/, check size against the server
cd /mnt/e/Ciencia/noturno/2024-dimitrov-liana-slidetags/sources
base="https://media.springernature.com/original/springer-static/esm/art%3A10.1038%2Fs41556-024-01469-w/MediaObjects/41556_2024_1469_"
for f in MOESM1_ESM.pdf MOESM3_ESM.pdf MOESM7_ESM.xlsx; do
	server=$(curl -sIL "${base}${f}" | grep -i '^content-length' | tail -1 | tr -dc '0-9')
	curl -sL -o "$f" "${base}${f}"
	local_size=$(stat -c %s "$f")
	echo "$f server=$server local=$local_size md5=$(md5sum "$f" | cut -d' ' -f1)"
done
cp /mnt/e/Ciencia/noturno/triagem-2026-10-26/dl/lm/benchmark_slideseq.ipynb /mnt/e/Ciencia/noturno/triagem-2026-10-26/dl/lm/utils.py .
sha256sum benchmark_slideseq.ipynb utils.py
