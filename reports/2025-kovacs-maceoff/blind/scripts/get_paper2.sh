#!/bin/bash
cd /mnt/e/Ciencia/noturno/2025-kovacs-maceoff-cego/paper
for v in v1 v3 v4; do curl -sSL -o arxiv_2312.15211$v.pdf https://arxiv.org/pdf/2312.15211$v; echo "$v rc=$?"; done
which pdftotext pdfinfo
for f in *.pdf; do pdfinfo $f | grep Pages; pdftotext -layout $f ${f%.pdf}.txt; done
sha256sum *.pdf
