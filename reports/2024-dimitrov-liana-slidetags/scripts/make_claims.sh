#!/bin/bash
# Build claims.json, then freeze it with its sha256 and the time
cd /mnt/e/Ciencia/noturno/2024-dimitrov-liana-slidetags
OMP_NUM_THREADS=4 nice -n 19 python3 -I scripts/make_claims.py /mnt/e/Ciencia/noturno/2024-dimitrov-liana-slidetags || exit 1
python3 -I -c "import json; d=json.load(open('claims.json', encoding='utf-8')); print([c['id'] for c in d['claims']])"
