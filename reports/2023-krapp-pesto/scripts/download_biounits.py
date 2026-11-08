# Download PDB-format biounit files from files.wwpdb.org, with size check (Content-Length) and gzip check
# Usage: python -I download_biounits.py <out_dir> <manifest.tsv> <id:mode> ...   mode = all (pdb1..pdbN until 404) or first (pdb1 only)
import gzip
import hashlib
import os
import sys
import time
import urllib.error
import urllib.request

out_dir, manifest_path = sys.argv[1], sys.argv[2]
requests = [a.split(":") for a in sys.argv[3:]]
base = "https://files.wwpdb.org/pub/pdb/data/biounit/PDB/divided"


def fetch(url):
	# Return (status, bytes, content_length)
	for attempt in range(3):
		try:
			with urllib.request.urlopen(url, timeout=60) as resp:
				data = resp.read()
				return 200, data, int(resp.headers.get("Content-Length", -1))
		except urllib.error.HTTPError as e:
			if e.code == 404:
				return 404, b"", -1
			time.sleep(2)
		except Exception:
			time.sleep(2)
	return -1, b"", -1


done = set()
if os.path.exists(manifest_path):
	for line in open(manifest_path):
		done.add(line.split("\t")[0])
manifest = open(manifest_path, "a")
for pdbid, mode in requests:
	pdbid = pdbid.lower()
	mid = pdbid[1:3]
	os.makedirs(f"{out_dir}/{mid}", exist_ok=True)
	n = 1
	while True:
		name = f"{pdbid}.pdb{n}.gz"
		if name in done:
			n += 1
			if mode == "first":
				break
			continue
		status, data, clen = fetch(f"{base}/{mid}/{name}")
		if status == 404:
			manifest.write(f"{name}\t404\t\t\t\n")
			break
		if status != 200:
			manifest.write(f"{name}\tFAILED\t\t\t\n")
			break
		# Size check against the server header, then a full gzip decode
		if clen != len(data):
			manifest.write(f"{name}\tSIZE_MISMATCH\t{len(data)}\t{clen}\t\n")
			break
		gzip.decompress(data)
		open(f"{out_dir}/{mid}/{name}", "wb").write(data)
		manifest.write(f"{name}\t200\t{len(data)}\t{clen}\t{hashlib.md5(data).hexdigest()}\n")
		manifest.flush()
		if mode == "first":
			break
		n += 1
manifest.close()
