#!/bin/bash
# Files written before the power cut could hold bad pages (the scores zip did: 128 KiB).
# Re-fetch the bytes that existed before the cut and compare byte by byte
W=/mnt/e/Ciencia/meio/2023-notin-proteingym/data/weights
F=https://dl.fbaipublicfiles.com/fair-esm/models
check() # name bytes
{
	curl -sS -r 0-$(($2 - 1)) $F/$1 | cmp - <(head -c $2 $W/$1) && echo "SAME first $2 bytes of $1" || echo "DIFF $1"
}
check esm2_t6_8M_UR50D.pt 30099493
check esm2_t12_35M_UR50D.pt 134095705
check esm2_t30_150M_UR50D.pt 592774773
check esm1b_t33_650M_UR50S.pt 1700000000
