"""Can every small-molecule Fig. 2b name be rebuilt from the deposited file?

Name shape is <id>_<chain><ligand>.pdb, e.g. 1a28_ASTR.pdb = entry 1a28, chain A,
ligand STR. This checks, by plain text, that the named ligand really sits in the
named chain of the asymmetric unit, and counts the cases where it does not.
"""

import collections
import json
import os

ROOT = "E:/Ciencia/pipeline/2025-dauparas-ligandmpnn"
ASYM = ROOT + "/data/structures/asym"

names = json.load(open(ROOT + "/sources/fig2b_names.json"))["small_molecule"]
print("names:", len(names))

lens = collections.Counter(len(n) for n in names)
print("name lengths (with .pdb):", dict(lens))


def parse_name(n):
    stem = n[:-4] if n.endswith(".pdb") else n
    return stem[:4], stem[5], stem[6:]


def read_het(path):
    """resname -> set of chain ids, for every non-water HETATM; plus protein chains."""
    het = collections.defaultdict(set)
    prot_chains = collections.Counter()
    with open(path, "r", errors="replace") as fh:
        for line in fh:
            rec = line[:6]
            if rec == "HETATM":
                resn = line[17:20].strip()
                if resn in ("HOH", "DOD", "WAT"):
                    continue
                het[resn].add(line[21])
            elif rec == "ATOM  ":
                prot_chains[line[21]] += 1
    return het, prot_chains


ok = 0
lig_elsewhere = []
lig_missing = []
chain_missing = []
multi_copy = []

for n in names:
    pid, chain, lig = parse_name(n)
    path = os.path.join(ASYM, pid + ".pdb")
    if not os.path.exists(path):
        lig_missing.append((n, "no file"))
        continue
    het, prot = read_het(path)
    if chain not in prot:
        chain_missing.append((n, sorted(prot)[:6]))
    if lig not in het:
        lig_missing.append((n, sorted(het)[:8]))
    elif chain in het[lig]:
        ok += 1
        if len(het[lig]) > 1:
            multi_copy.append((n, sorted(het[lig])))
    else:
        lig_elsewhere.append((n, sorted(het[lig])))

print("ligand present in the named chain :", ok)
print("ligand present but another chain  :", len(lig_elsewhere), lig_elsewhere[:10])
print("ligand resname not in file        :", len(lig_missing), lig_missing[:10])
print("named protein chain absent        :", len(chain_missing), chain_missing[:10])
print("ligand copies in >1 chain (kept named chain):", len(multi_copy), multi_copy[:10])
