#!/bin/bash
set -u
cd /mnt/e/Ciencia/noturno/2025-kovacs-maceoff-cego/paper
curl -sSL -o arxiv_2312.15211.pdf https://arxiv.org/pdf/2312.15211 ; echo "arxiv rc=$?"
curl -sSL -o arxiv_abs.html https://arxiv.org/abs/2312.15211 ; echo "abs rc=$?"
curl -sSL -A "Mozilla/5.0" -w "%{http_code}\n" -o acs_si.html "https://pubs.acs.org/doi/suppl/10.1021/jacs.4c07099" ; echo "acs rc=$?"
ls -la
file *
