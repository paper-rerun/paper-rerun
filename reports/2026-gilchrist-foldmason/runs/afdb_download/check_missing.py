# For every member whose model_v6 returned 404, ask the AFDB API and UniProt what happened to it
# Usage: python3 -I check_missing.py <download.log> <out.tsv>
import json
import sys
import time
import urllib.request

LOG, OUT = sys.argv[1], sys.argv[2]
HEADERS = {"User-Agent": "Mozilla/5.0 (paper-rerun reproduction)"}
accessions = [line.split("AF-")[1].split("-F1")[0] for line in open(LOG) if line.startswith("404 ")]

def get_json(url):
	for attempt in range(5):
		try:
			with urllib.request.urlopen(urllib.request.Request(url, headers=HEADERS), timeout=60) as response:
				return json.loads(response.read() or b"{}")
		except urllib.error.HTTPError as error:
			if error.code == 404:
				return {}
			time.sleep(5 * 2 ** attempt)
		except Exception:
			time.sleep(5 * 2 ** attempt)
	return {"error": "failed"}

with open(OUT, "w") as out:
	out.write("accession\tafdb_api\tuniprot_entry_type\tuniprot_inactive_reason\n")
	for acc in accessions:
		afdb = get_json(f"https://alphafold.ebi.ac.uk/api/prediction/{acc}")
		afdb_state = "none" if not afdb else ("versions " + ",".join(map(str, afdb[0].get("allVersions", []))) if isinstance(afdb, list) else "unexpected")
		uniprot = get_json(f"https://rest.uniprot.org/uniprotkb/{acc}?format=json&fields=accession")
		reason = uniprot.get("inactiveReason", {})
		out.write(f"{acc}\t{afdb_state}\t{uniprot.get('entryType', 'NA')}\t{reason.get('inactiveReasonType', '')}:{reason.get('deletedReason', '')}\n")
		out.flush()
		time.sleep(0.3)
print("checked", len(accessions))
