"""Turn out/comparison.csv into the markdown blocks REPORT.md needs."""
import csv, os
from collections import Counter, defaultdict

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
rows = list(csv.DictReader(open(os.path.join(HERE, 'out', 'comparison.csv'), encoding='utf-8')))

ORDER = ['igw', 'sigw-delta', 'sigw-gauss', 'sigw-box', 'pt-bubble', 'pt-sound',
         'stable-c', 'stable-k', 'stable-m', 'stable-n', 'meta-l', 'meta-ls',
         'super', 'dw-sm', 'dw-dr']
KINDS = ['bayes_mean', 'bayes_sd', 'maxpost', 'ci68_lo', 'ci68_hi']

out = []
out.append('### Verdict counts by cell type\n')
out.append('| cell type | reproduced | near-miss | not reproduced | total |')
out.append('|---|---|---|---|---|')
for k in KINDS:
    sub = [r for r in rows if r['cell'] == k]
    c = Counter(r['verdict'] for r in sub)
    out.append('| %s | %d | %d | %d | %d |' % (k, c['reproduced'], c['near-miss'],
                                               c['not-reproduced'], len(sub)))
c = Counter(r['verdict'] for r in rows)
out.append('| **all** | %d | %d | %d | %d |' % (c['reproduced'], c['near-miss'],
                                                c['not-reproduced'], len(rows)))

out.append('\n### Verdict counts by model\n')
out.append('| model | reproduced | near-miss | not reproduced |')
out.append('|---|---|---|---|')
for m in ORDER:
    sub = [r for r in rows if r['model'] == m]
    c = Counter(r['verdict'] for r in sub)
    out.append('| %s | %d | %d | %d |' % (m, c['reproduced'], c['near-miss'], c['not-reproduced']))

out.append('\n### Every cell that is not "reproduced"\n')
out.append('| model | param | analysis | cell | printed | measured | delta | verdict | detail |')
out.append('|---|---|---|---|---|---|---|---|---|')
for r in rows:
    if r['verdict'] == 'reproduced':
        continue
    out.append('| %s | %s | %s | %s | %s | %s | %s | %s | %s |' % (
        r['model'], r['param'], r['analysis'], r['cell'], r['printed'],
        r['measured'], r['delta'], r['verdict'], r['note'].replace('|', '/')))

out.append('\n### Full cell-by-cell table\n')
out.append('| model | param | analysis | cell | printed | measured | delta | verdict |')
out.append('|---|---|---|---|---|---|---|---|')
for m in ORDER:
    for r in rows:
        if r['model'] != m:
            continue
        out.append('| %s | %s | %s | %s | %s | %s | %s | %s |' % (
            r['model'], r['param'], r['analysis'], r['cell'], r['printed'],
            r['measured'], r['delta'], r['verdict']))

open(os.path.join(HERE, 'out', 'report_tables.md'), 'w', encoding='utf-8').write('\n'.join(out) + '\n')
print('\n'.join(out[:40]))
print('... wrote out/report_tables.md, %d rows' % len(rows))
