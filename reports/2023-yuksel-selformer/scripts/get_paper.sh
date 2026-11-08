#!/bin/bash
# Keep a copy of both versions of the paper: the published MLST article and arXiv v2 (the triage used arXiv)
set -u
S=/mnt/e/Ciencia/noturno/2023-yuksel-selformer/sources
mkdir -p "$S"
UA='Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0 Safari/537.36'
curl -sL -A "$UA" "https://iopscience.iop.org/article/10.1088/2632-2153/acdb30/pdf" -o "$S/mlst_acdb30.pdf"
curl -sL "https://arxiv.org/pdf/2304.04662v2" -o "$S/arxiv_2304.04662v2.pdf"
for f in "$S"/*.pdf; do
	echo "$f $(stat -c%s "$f") $(head -c4 "$f" | tr -d '\0')"
done
sha256sum "$S"/*.pdf
