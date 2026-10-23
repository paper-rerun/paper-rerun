"""Fetch the deposited structures for the three test splits.

Two flavours per entry, because the paper leaves the choice open: the asymmetric
unit (<id>.pdb) and biological assembly 1 (<id>.pdb1). The run stage picks one and
records it. Entries too big for PDB format only exist as mmCIF; those land in the
manifest as missing so the run stage sees them instead of guessing.
"""

import gzip
import json
import os
import sys
import time
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor

ROOT = "/mnt/e/Ciencia/pipeline/2025-dauparas-ligandmpnn"
REPO = ROOT + "/repo/training"
OUT = ROOT + "/data/structures"
BASE = "https://files.rcsb.org/download/"

SPLITS = {
    "small_molecule": "test_small_molecule.json",
    "nucleotide": "test_nucleotide.json",
    "metal": "test_metal.json",
}


def fetch(url, tries=4):
    last = None
    for attempt in range(tries):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "repro-pipeline/1.0"})
            with urllib.request.urlopen(req, timeout=90) as resp:
                return resp.read()
        except urllib.error.HTTPError as err:
            if err.code == 404:
                return None
            last = err
        except Exception as err:  # network hiccup, worth another go
            last = err
        time.sleep(2 * (attempt + 1))
    raise RuntimeError("%s failed: %s" % (url, last))


def one(entry):
    pdb_id, flavour = entry
    suffix = ".pdb" if flavour == "asym" else ".pdb1"
    dest = os.path.join(OUT, flavour, pdb_id + ".pdb")
    if os.path.exists(dest) and os.path.getsize(dest) > 0:
        return pdb_id, flavour, "have"

    raw = fetch(BASE + pdb_id + suffix + ".gz")
    if raw is None:
        raw = fetch(BASE + pdb_id + suffix)
        if raw is None:
            return pdb_id, flavour, "missing"
    else:
        raw = gzip.decompress(raw)

    tmp = dest + ".part"
    with open(tmp, "wb") as fh:
        fh.write(raw)
    os.replace(tmp, dest)
    return pdb_id, flavour, "ok"


def main():
    ids = {}
    for split, name in SPLITS.items():
        ids[split] = json.load(open(os.path.join(REPO, name)))
        print(split, len(ids[split]))

    unique = sorted({i for v in ids.values() for i in v})
    print("unique entries:", len(unique))

    for flavour in ("asym", "biounit1"):
        os.makedirs(os.path.join(OUT, flavour), exist_ok=True)

    jobs = [(i, f) for f in ("asym", "biounit1") for i in unique]
    results = {"asym": {}, "biounit1": {}}
    with ThreadPoolExecutor(max_workers=6) as pool:
        for n, (pdb_id, flavour, state) in enumerate(pool.map(one, jobs), 1):
            results[flavour][pdb_id] = state
            if n % 100 == 0:
                print("...", n, "of", len(jobs), flush=True)

    manifest = {
        "source": BASE,
        "splits": {k: ids[k] for k in ids},
        "unique_entries": unique,
        "status": results,
        "missing": {f: sorted(k for k, v in results[f].items() if v == "missing") for f in results},
    }
    with open(os.path.join(OUT, "manifest.json"), "w") as fh:
        json.dump(manifest, fh, indent=1)

    for flavour in results:
        counts = {}
        for state in results[flavour].values():
            counts[state] = counts.get(state, 0) + 1
        print(flavour, counts)
        if manifest["missing"][flavour]:
            print("  missing:", " ".join(manifest["missing"][flavour]))


if __name__ == "__main__":
    sys.exit(main())
