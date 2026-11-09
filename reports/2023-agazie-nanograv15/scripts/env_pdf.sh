#!/bin/bash
set -e
W=/mnt/e/Ciencia/noturno/2023-agazie-nanograv15
export UV_CACHE_DIR=$W/env/uv-cache
cd $W/env
uv venv -p 3.10 pdfvenv
uv pip install -p pdfvenv/bin/python pypdf==4.3.1
pdfvenv/bin/python -I -c "
import pypdf
r=pypdf.PdfReader('$W/sources/paper_arxiv_2306.16213.pdf')
print(len(r.pages))
open('$W/sources/paper.txt','w').write('\n'.join(f'=== PAGE {i+1} ===\n'+p.extract_text() for i,p in enumerate(r.pages)))
"
