#!/bin/bash
# Freeze claims.json: write its sha256 and the time; from here claims.json must not change
cd /mnt/e/Ciencia/noturno/2024-dimitrov-liana-slidetags
hash=$(sha256sum claims.json | cut -d' ' -f1)
now=$(date -u +%Y-%m-%dT%H:%M:%SZ)
printf '%s  claims.json\nfrozen_at_utc: %s\n' "$hash" "$now" > claims.sha256
chmod a-w claims.json
cat claims.sha256
sha256sum -c <(head -1 claims.sha256)
