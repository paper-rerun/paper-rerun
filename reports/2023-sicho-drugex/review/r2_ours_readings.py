"""Our own 100k samples under the wider reading menu, incl. dedup-then-validate."""
import gzip, json, sys
from rdkit import Chem, RDLogger
RDLogger.DisableLog("rdApp.*")
out = {}
for name, path in (("ChEMBL 27 LSTM", sys.argv[1]), ("ChEMBL 31 GRU", sys.argv[2])):
    with gzip.open(path, "rt", encoding="utf-8") as fh:
        smis = [l.rstrip("\n") for l in fh]
    n = len(smis)
    raw = set(smis); valid_raw = set(); canon = set(); nvalid = 0
    for s in smis:
        m = Chem.MolFromSmiles(s)
        if m is None: continue
        c = Chem.MolToSmiles(m)
        if "." in c: continue
        nvalid += 1; valid_raw.add(s); canon.add(c)
    out[name] = {"n": n, "n_valid": nvalid, "distinct_raw": len(raw),
      "distinct_valid_raw": len(valid_raw), "distinct_canon": len(canon),
      "V:parseable_single_frag": nvalid/n,
      "U:distinct_canon_over_valid": len(canon)/nvalid,
      "U:distinct_raw_over_n": len(raw)/n,
      "U:distinct_canon_over_n": len(canon)/n,
      "U:distinct_valid_raw_over_distinct_raw": len(valid_raw)/len(raw),
      "U:distinct_canon_over_distinct_raw": len(canon)/len(raw),
      "U:distinct_valid_raw_over_valid": len(valid_raw)/nvalid}
print(json.dumps(out, indent=1))
