"""Compute validity and uniqueness from a file of raw sampled SMILES (one per line).

Primary definitions (pre-registered in claims.json):
  validity = n_valid / n_sampled, valid = no '.' in the string AND Chem.MolFromSmiles parses
             (this is SmilesChecker.checkSmiles(no_multifrag_smiles=True) from the release)
  uniqueness = distinct canonical SMILES among valid / n_valid
Secondary variants are reported alongside.
"""
import sys, json
from rdkit import Chem, RDLogger
RDLogger.DisableLog('rdApp.*')

path = sys.argv[1]
lines = [l.rstrip('\n') for l in open(path, encoding='utf-8')]
n = len(lines)

canon_strict, canon_loose = [], []
n_valid_strict = n_valid_loose = 0
raw_valid_strict = []
n_empty = 0
for s in lines:
    if s == '':
        n_empty += 1
    mol = Chem.MolFromSmiles(s) if s else None
    if mol is not None:
        n_valid_loose += 1
        canon_loose.append(Chem.MolToSmiles(mol))
        if s.count('.') == 0:
            n_valid_strict += 1
            canon_strict.append(Chem.MolToSmiles(mol))
            raw_valid_strict.append(s)

out = {
    'file': path,
    'n_sampled': n,
    'n_empty_strings': n_empty,
    'n_valid_primary': n_valid_strict,
    'validity_primary': round(n_valid_strict / n, 6),
    'n_unique_canonical_among_valid': len(set(canon_strict)),
    'uniqueness_primary': round(len(set(canon_strict)) / n_valid_strict, 6) if n_valid_strict else None,
    'variants': {
        'uniqueness_over_n_sampled': round(len(set(canon_strict)) / n, 6),
        'uniqueness_raw_strings_over_valid': round(len(set(raw_valid_strict)) / n_valid_strict, 6) if n_valid_strict else None,
        'validity_multifrag_allowed': round(n_valid_loose / n, 6),
        'uniqueness_multifrag_allowed': round(len(set(canon_loose)) / n_valid_loose, 6) if n_valid_loose else None,
    },
}
print(json.dumps(out, indent=2))
with open(path + '.scores.json', 'w') as fh:
    json.dump(out, fh, indent=2)
