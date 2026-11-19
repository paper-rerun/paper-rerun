"""For the two in-scope RNN rows, recompute every plausible validity/uniqueness from the
authors' own per-molecule dump and cross-tab their Valid/Unique/Novel flags."""
import sys, lzma, collections, json
from rdkit import Chem, RDLogger
RDLogger.DisableLog('rdApp.*')

path = sys.argv[1]
want = {('ChEMBL 27', 'sequence LSTM RNN'), ('ChEMBL 31', 'sequence GRU RNN')}
groups = collections.defaultdict(lambda: dict(rows=[], xtab=collections.Counter()))
with lzma.open(path, 'rt', encoding='utf-8', newline='') as f:
    header = f.readline().rstrip('\n').split('\t')
    idx = {k: i for i, k in enumerate(header)}
    for line in f:
        line = line.rstrip('\n')
        if not line:
            continue
        p = line.split('\t')
        if len(p) < len(header):
            continue
        ds, ver, mach = p[idx['dataset']], p[idx['DrugEx version']], p[idx['Machine']]
        if (ds, ver) not in want or mach != 'M01':
            continue
        g = groups[(ds, ver, mach)]
        g['rows'].append((p[idx['SMILES']], p[idx['Valid']], p[idx['Unique']], p[idx['Novel']]))

out = []
for k, g in groups.items():
    rows = g['rows']
    n = len(rows)
    xt = collections.Counter((v, u) for _, v, u, _ in rows)
    smis = [s for s, v, u, _ in rows]
    flagged_valid = [s for s, v, u, _ in rows if v == '1.0']
    # recompute validity with rdkit on the dumped strings
    rd_valid_strict, rd_valid_loose = [], []
    for s in smis:
        m = Chem.MolFromSmiles(s) if s.strip() else None
        if m is not None:
            rd_valid_loose.append(Chem.MolToSmiles(m))
            if s.count('.') == 0:
                rd_valid_strict.append(Chem.MolToSmiles(m))
    nv = len(rd_valid_strict)
    out.append({
        'group': k, 'n': n,
        'mean_flag_Valid': round(sum(1 for _, v, _, _ in rows if v == '1.0') / n, 6),
        'mean_flag_Unique': round(sum(1 for _, _, u, _ in rows if u == '1') / n, 6),
        'xtab_Valid_Unique': {f'V={a},U={b}': c for (a, b), c in sorted(xt.items())},
        'rdkit_validity_strict_over_n': round(nv / n, 6),
        'rdkit_validity_loose_over_n': round(len(rd_valid_loose) / n, 6),
        'distinct_canon_among_valid': len(set(rd_valid_strict)),
        'uniq_distinct_over_nvalid': round(len(set(rd_valid_strict)) / nv, 6),
        'uniq_distinct_over_n': round(len(set(rd_valid_strict)) / n, 6),
        'distinct_raw_strings_over_n': round(len(set(smis)) / n, 6),
        'distinct_raw_strings_among_flagged_valid_over_nflagged': round(len(set(flagged_valid)) / len(flagged_valid), 6) if flagged_valid else None,
    })
print(json.dumps(out, indent=1, default=str))
