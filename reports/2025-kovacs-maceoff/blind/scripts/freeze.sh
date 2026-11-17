#!/bin/bash
cd /mnt/e/Ciencia/noturno/2025-kovacs-maceoff-cego
env/venv/bin/python -I scripts/make_claims.py
sha256sum claims.json > claims.json.sha256
date -u +%Y-%m-%dT%H:%M:%SZ > claims.frozen_at
cat claims.json.sha256 claims.frozen_at
