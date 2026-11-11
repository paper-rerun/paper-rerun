import json, hashlib, datetime, pathlib, sys
p = pathlib.Path(sys.argv[1])
d = json.loads(p.read_text(encoding='utf-8'))
now = datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')
d['meta']['frozen_at_utc'] = now
txt = json.dumps(d, indent=2, ensure_ascii=False, sort_keys=False)
p.write_text(txt, encoding='utf-8')
h = hashlib.sha256(p.read_bytes()).hexdigest()
pathlib.Path(p.parent / 'claims.sha256').write_text(f"{h}  claims.json\nfrozen_at_utc {now}\n", encoding='utf-8')
print(h, now)
