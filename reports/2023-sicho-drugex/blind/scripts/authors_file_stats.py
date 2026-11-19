import sys, lzma, collections, json
path = sys.argv[1]
agg = collections.defaultdict(lambda: dict(n=0, valid=0, unique=0, novel=0, nonempty_smiles=0, n_valid_missing=0))
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
        key = (p[idx['Machine']], p[idx['dataset']], p[idx['DrugEx version']], p[idx['fragmentation method']])
        a = agg[key]
        a['n'] += 1
        for col, name in (('Valid', 'valid'), ('Unique', 'unique'), ('Novel', 'novel')):
            v = p[idx[col]]
            try:
                a[name] += float(v)
            except ValueError:
                a['n_valid_missing'] += 1
        if p[idx['SMILES']].strip():
            a['nonempty_smiles'] += 1
rows = []
for k in sorted(agg):
    a = agg[k]
    rows.append(dict(machine=k[0], dataset=k[1], version=k[2], frag=k[3], n=a['n'],
                     mean_valid=round(a['valid'] / a['n'], 6),
                     mean_unique=round(a['unique'] / a['n'], 6),
                     mean_novel=round(a['novel'] / a['n'], 6),
                     nonempty_smiles=a['nonempty_smiles']))
print(json.dumps(rows, indent=1))
