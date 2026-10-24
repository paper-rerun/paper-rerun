#!/bin/bash
cd /mnt/e/Ciencia/pipeline/2023-notin-proteingym/sources
for f in *.pdf; do pdftotext -layout "$f" "${f%.pdf}.txt"; echo "$f"; pdfinfo "$f" | grep Pages; done
