"""Post-hoc variants, added after inspecting the authors' own per-molecule dump.

The dump's 'Unique' flag equals (distinct raw sampled strings) / (all 100,000 rows),
invalid strings included. That is the authors' operational uniqueness, so measure it too.
"""
import sys, json
from rdkit import Chem, RDLogger
RDLogger.DisableLog('rdApp.*')
path = sys.argv[1]
lines = [l.rstrip('\n') for l in open(path, encoding='utf-8')]
n = len(lines)
nonempty = sum(1 for s in lines if s.strip())
canon = []
for s in lines:
    m = Chem.MolFromSmiles(s) if s and s.count('.') == 0 else None
    if m is not None:
        canon.append(Chem.MolToSmiles(m))
out = {
    'file': path, 'n': n,
    'authors_operational_validity_nonempty_over_n': round(nonempty / n, 6),
    'authors_operational_uniqueness_distinct_raw_over_n': round(len(set(lines)) / n, 6),
    'distinct_canonical_valid_over_n': round(len(set(canon)) / n, 6),
}
print(json.dumps(out, indent=2))
with open(path + '.extra.json', 'w') as fh:
    json.dump(out, fh, indent=2)
