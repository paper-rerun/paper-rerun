#!/bin/bash
set -e
cd /mnt/e/Ciencia/noturno/2023-agazie-nanograv15/sources
curl -fsSL -o paper_arxiv_2306.16213.pdf https://arxiv.org/pdf/2306.16213
ls -l paper_arxiv_2306.16213.pdf; sha256sum paper_arxiv_2306.16213.pdf
pip list 2>/dev/null | grep -i pdf; which pdftotext
