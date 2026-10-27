# Read Source Data Fig. 4 (paper's own numbers) with stdlib; write TSV and the per-score / per-method medians.
# This only extracts what the authors published, nothing of ours is computed here
import sys, zipfile, re, json, statistics, collections
import xml.etree.ElementTree as ET
sys.stdout.reconfigure(encoding='utf-8')
xlsx, out_tsv, out_json = sys.argv[1], sys.argv[2], sys.argv[3]
ns = {'m': 'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}
z = zipfile.ZipFile(xlsx)
shared = []
if 'xl/sharedStrings.xml' in z.namelist():
	for si in ET.fromstring(z.read('xl/sharedStrings.xml')).findall('m:si', ns):
		shared.append(''.join(t.text or '' for t in si.iter('{%s}t' % ns['m'])))
sheets = sorted(n for n in z.namelist() if re.match(r'xl/worksheets/sheet\d+\.xml', n))
table = []
for cell_row in ET.fromstring(z.read(sheets[0])).findall('.//m:row', ns):
	values = []
	for c in cell_row.findall('m:c', ns):
		v = c.find('m:v', ns)
		text = v.text if v is not None else ''
		if c.get('t') == 's':
			text = shared[int(text)]
		values.append(text)
	table.append(values)
print('sheets', sheets, 'rows', len(table))
header = table[0]
print('header', header)
rows = [dict(zip(header, r)) for r in table[1:] if any(r)]
with open(out_tsv, 'w', encoding='utf-8') as f:
	f.write('\t'.join(header) + '\n')
	for r in table[1:]:
		f.write('\t'.join(r) + '\n')
metrics = ['AUROC', 'Balanced Accuracy', 'Precision', 'Recall', 'F1', 'F1*', 'F1 (normalised)', 'F1* (normalised)', 'Positive Calls']
print(len(rows), 'rows;', sorted({r['Dataset'] for r in rows}))
print('example raw strings:', rows[0])

# Per score (AUROC, F1* normalised) and per method (BA, F1 normalised, one value per dataset)
per_score = collections.defaultdict(lambda: collections.defaultdict(list))
per_method = collections.defaultdict(lambda: collections.defaultdict(dict))
for r in rows:
	for m in ['AUROC', 'F1* (normalised)']:
		per_score[m][r['Method'] + ' | ' + r['Score']].append(float(r[m]))
	for m in ['Balanced Accuracy', 'F1 (normalised)', 'Precision', 'Recall', 'F1', 'Positive Calls']:
		previous = per_method[m][r['Method']].get(r['Dataset'])
		value = float(r[m])
		if previous is not None and previous != value:
			print('WARNING per-method value differs between score rows', r['Method'], r['Dataset'], m, previous, value)
		per_method[m][r['Method']][r['Dataset']] = value
result = {}
for m, d in per_score.items():
	result[m] = sorted(((k, statistics.median(v), len(v)) for k, v in d.items()), key=lambda t: -t[1])
for m, d in per_method.items():
	result[m] = sorted(((k, statistics.median(v.values()), len(v)) for k, v in d.items()), key=lambda t: -t[1])
for m in ['AUROC', 'Balanced Accuracy', 'F1 (normalised)', 'F1* (normalised)']:
	print('==', m)
	for k, med, n in result[m]:
		print(f'  {k:40s} {med!r}  n={n}')

# Spearman between Positive Calls and each metric over the 75 rows (SI quotes rho = 0.765 for F1)
def average_ranks(x):
	order = sorted(range(len(x)), key=lambda i: x[i])
	ranks = [0.0] * len(x)
	i = 0
	while i < len(order):
		j = i
		while j + 1 < len(order) and x[order[j + 1]] == x[order[i]]:
			j += 1
		for k in range(i, j + 1):
			ranks[order[k]] = (i + j) / 2.0 + 1
		i = j + 1
	return ranks
def spearman(a, b):
	ra, rb = average_ranks(a), average_ranks(b)
	return statistics.correlation(ra, rb)
pc = [float(r['Positive Calls']) for r in rows]
spear = {m: spearman(pc, [float(r[m]) for r in rows]) for m in metrics if m != 'Positive Calls'}
print('Spearman vs Positive Calls:', {k: round(v, 4) for k, v in spear.items()})
json.dump({'medians': result, 'spearman_vs_positive_calls': spear, 'n_rows': len(rows)}, open(out_json, 'w', encoding='utf-8'), indent=1, ensure_ascii=False)
