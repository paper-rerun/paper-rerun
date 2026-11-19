"""Shape of the invalid strings: ours vs the authors' deposited rows (ChEMBL 27 LSTM)."""
import collections, gzip, lzma, sys
from rdkit import Chem, RDLogger
RDLogger.DisableLog("rdApp.*")
PROBE = "C=CCOCc1ccccc1)OCc1ccccc1"

def shape(smis):
    c = collections.Counter(); n = 0; probe = 0; unbal = 0
    for s in smis:
        if Chem.MolFromSmiles(s) is not None: continue
        n += 1
        if s == PROBE: probe += 1
        if s.count(")") > s.count("("): unbal += 1
        c[s[-11:]] += 1
    return n, probe, unbal, c.most_common(5)

with gzip.open(sys.argv[1], "rt", encoding="utf-8") as fh:
    print("ours c27 invalid:", shape(l.rstrip("\n") for l in fh))

rows = collections.defaultdict(list)
with lzma.open(sys.argv[2], "rt", encoding="utf-8") as fh:
    header = fh.readline().rstrip("\n").split("\t")
    col = {n: i for i, n in enumerate(header)}
    for line in fh:
        f = line.rstrip("\n").split("\t")
        if len(f) != len(header): continue
        if (f[col["dataset"]], f[col["DrugEx version"]]) != ("ChEMBL 27", "sequence LSTM RNN"): continue
        if f[col["Machine"]] != "M01": continue
        rows["M01"].append(f[col["SMILES"]])
print("their M01 rows:", len(rows["M01"]))
print("their M01 invalid:", shape(rows["M01"]))
