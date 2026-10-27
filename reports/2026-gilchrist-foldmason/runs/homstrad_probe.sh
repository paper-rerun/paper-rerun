#!/bin/bash
# Probe the HOMSTRAD server and the Wayback CDX index for the release the authors used, with timestamps
# Usage: bash homstrad_probe.sh > homstrad_probe.log 2>&1
TARBALL=https://homstrad.mizuguchilab.org/homstrad/data/homstrad_with_PDB_2024_Dec_1.tar.gz
CDX="https://web.archive.org/cdx/search/cdx?url=homstrad.mizuguchilab.org/homstrad/data/homstrad_with_PDB_2024_Dec_1.tar.gz&output=json&limit=5"
# Server: headers only, nothing is saved
for URL in https://homstrad.mizuguchilab.org/ "$TARBALL"
do
	echo "=== $(date -u +%FT%TZ) HEAD $URL"
	curl -sS -I --max-time 30 -w 'http_code %{http_code}\n' "$URL" 2>&1 | head -20
	echo "=== $(date -u +%FT%TZ) curl exit ${PIPESTATUS[0]}"
done
# Wayback index: small JSON answer, printed whole
echo "=== $(date -u +%FT%TZ) GET $CDX"
curl -sS --max-time 30 -w '\nhttp_code %{http_code}\n' "$CDX" 2>&1 | head -c 3000
echo "=== $(date -u +%FT%TZ) curl exit ${PIPESTATUS[0]}"
