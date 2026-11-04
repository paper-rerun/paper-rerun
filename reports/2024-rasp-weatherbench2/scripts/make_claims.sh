cd /mnt/e/Ciencia/noturno/2024-rasp-weatherbench2
python3 -I scripts/make_claims.py claims.json
python3 -I -m json.tool claims.json > /dev/null && echo json_ok
SUM=$(sha256sum claims.json | cut -d' ' -f1)
NOW=$(date -u +%Y-%m-%dT%H:%M:%SZ)
printf '%s  claims.json\n# frozen at %s (UTC), pre-registration stage, before any computation\n' "$SUM" "$NOW" > claims.sha256
cat claims.sha256
