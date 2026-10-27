# Sequential AFDB downloader for the 160 benchmark clusters (aria2c with 4 connections hit HTTP 429)
# Fetches model_v6, saves under the authors' v4 file name, checks every file against the server Content-Length
# Restartable: a file is skipped only if its size matches the size recorded in sizes.tsv
# Usage: python3 -I fetch_afdb.py <aria_list.txt> <sizes.tsv>
import base64
import gzip
import hashlib
import os
import sys
import time
import urllib.error
import urllib.request

LIST, SIZES = sys.argv[1], sys.argv[2]
HEADERS = {"User-Agent": "Mozilla/5.0 (paper-rerun reproduction; contact via github.com/paper-rerun)", "Accept-Encoding": "gzip"}

# Parse the aria2c input list: url line followed by dir= and out= lines
jobs = []
lines = open(LIST).read().splitlines()
for i in range(0, len(lines), 3):
	url = lines[i].strip()
	folder = lines[i + 1].split("=", 1)[1]
	name = lines[i + 2].split("=", 1)[1]
	jobs.append((url, os.path.join(folder, name)))

recorded = {}
if os.path.exists(SIZES):
	for row in open(SIZES):
		path, size = row.rstrip("\n").split("\t")[:2]
		recorded[path] = int(size)

log = open(SIZES, "a")
failed = []
for n, (url, path) in enumerate(jobs, 1):
	if path in recorded and os.path.exists(path) and os.path.getsize(path) == recorded[path]:
		continue
	os.makedirs(os.path.dirname(path), exist_ok=True)
	for attempt in range(8):
		try:
			# The server sends the stored gzip object chunked, with no Content-Length for the plain file
			# So we take the gzip bytes and check them against the stored size and md5 the server reports
			with urllib.request.urlopen(urllib.request.Request(url, headers=HEADERS), timeout=60) as response:
				expected = int(response.headers["x-goog-stored-content-length"])
				hashes = response.headers.get_all("x-goog-hash")
				encoding = response.headers.get("Content-Encoding")
				data = response.read()
			expected_md5 = [h.split("=", 1)[1] for h in hashes if h.startswith("md5=")][0]
			got_md5 = base64.b64encode(hashlib.md5(data).digest()).decode()
			if encoding != "gzip" or len(data) != expected or got_md5 != expected_md5:
				raise IOError(f"bad transfer: encoding {encoding} size {len(data)}/{expected} md5 {got_md5}/{expected_md5}")
			pdb = gzip.decompress(data)
			with open(path + ".part", "wb") as handle:
				handle.write(pdb)
			os.replace(path + ".part", path)
			log.write(f"{path}\t{len(pdb)}\t{url}\t{expected}\t{expected_md5}\n")
			log.flush()
			break
		except urllib.error.HTTPError as error:
			if error.code == 404:
				print("404", url, flush=True)
				failed.append(url)
				break
			# 429 or 5xx: back off and retry
			time.sleep(min(120, 5 * 2 ** attempt))
		except Exception as error:
			print("retry", url, error, flush=True)
			time.sleep(min(120, 5 * 2 ** attempt))
	else:
		print("gave up", url, flush=True)
		failed.append(url)
	# Be polite to the AFDB server
	time.sleep(0.3)
	if n % 200 == 0:
		print("progress", n, len(jobs), flush=True)

print("done", len(jobs), "failed", len(failed), flush=True)
for url in failed:
	print("FAILED", url)
