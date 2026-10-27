# For every member whose model_v6 returned 404, ask the file server for model_v1..v5 (HEAD only, nothing saved)
# Sequential with 0.3 s between requests, to stay polite after the 429s of the first download attempt
# Usage: python3 -I probe_versions.py <missing_status.tsv> <out.tsv>
import sys
import time
import urllib.error
import urllib.request

STATUS, OUT = sys.argv[1], sys.argv[2]
HEADERS = {"User-Agent": "Mozilla/5.0 (paper-rerun reproduction; contact via github.com/paper-rerun)"}
accessions = [row.split("\t")[0] for row in open(STATUS).read().splitlines()[1:]]

def head_code(url):
	for attempt in range(5):
		try:
			request = urllib.request.Request(url, headers=HEADERS, method="HEAD")
			with urllib.request.urlopen(request, timeout=60) as response:
				return str(response.status)
		except urllib.error.HTTPError as error:
			# 429 and 5xx get a retry, anything else is the answer
			if error.code != 429 and error.code < 500:
				return str(error.code)
		except Exception:
			pass
		time.sleep(5 * 2 ** attempt)
	return "failed"

with open(OUT, "w") as out:
	out.write("accession\tv1\tv2\tv3\tv4\tv5\n")
	for acc in accessions:
		codes = []
		for version in range(1, 6):
			codes.append(head_code(f"https://alphafold.ebi.ac.uk/files/AF-{acc}-F1-model_v{version}.pdb"))
			time.sleep(0.3)
		out.write(acc + "\t" + "\t".join(codes) + "\n")
		out.flush()
print("probed", len(accessions), time.strftime("%Y-%m-%dT%H:%M:%S"))
