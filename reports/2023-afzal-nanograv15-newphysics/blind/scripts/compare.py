"""Cell-by-cell comparison of the printed Table 4 against the recount.

Reads the frozen out/table4_printed.json for the numbers, and re-reads main.tex only
to recover how many decimals each cell was printed with (needed for the tolerance in
PREREG.md section 5). The frozen parser is not modified.
"""
import csv, json, os, re, sys

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BS = chr(92)
printed = json.load(open(os.path.join(HERE, 'out', 'table4_printed.json')))

# ---- recover printed precision from the LaTeX ------------------------------------
tex = open(os.path.join(HERE, 'arxiv-src', 'main.tex'), encoding='utf-8', errors='replace').read().splitlines()
start = next(i for i, l in enumerate(tex) if 'tab:list}' in l and 'caption' in l)
end = next(i for i, l in enumerate(tex[start:], start) if l.strip().startswith('\\bottomrule'))
raw_rows = []
for raw in tex[start + 1:end]:
    line = raw.strip()
    if '\\multicolumn{8}' in line or not line:
        continue
    body = re.sub(BS + BS + BS + BS + r'.*$', '', line)
    cols = body.split('&')
    if len(cols) != 8:
        continue
    if not cols[0].strip().strip('$').strip():
        continue
    raw_rows.append([c.strip() for c in cols])
assert len(raw_rows) == len(printed), (len(raw_rows), len(printed))


def decimals(tok):
    m = re.search(r'-?\d+\.(\d+)', tok)
    return len(m.group(1)) if m else 0


def split_pm(cell):
    parts = re.split(BS + BS + r'pm', cell)
    return [p for p in parts]


def tol_for(d, kind):
    if kind == 'maxpost':
        return 0.1
    return 0.6 * 10.0 ** (-d) if d > 0 else 0.6


def verdict(delta, tol, d, kind):
    if delta is None:
        return 'nodata'
    if abs(delta) <= tol:
        return 'reproduced'
    near = 3 * 10.0 ** (-d) if d > 0 else 3.0
    if kind == 'maxpost':
        near = 0.3
    if abs(delta) <= near:
        return 'near-miss'
    return 'not-reproduced'


# ---- measured --------------------------------------------------------------------
cells_dir = os.path.join(HERE, 'out', 'cells')
measured = {}
for fn in os.listdir(cells_dir):
    if not fn.endswith('.json'):
        continue
    d = json.load(open(os.path.join(cells_dir, fn)))
    measured[(d['model'], d['analysis'])] = d

rows_out = []
missing = []
for prow, rrow in zip(printed, raw_rows):
    model, param = prow['model'], prow['param']
    for analysis, suf in (('NP', '_NP'), ('NPSMBHB', '_NPSMBHB')):
        key = (model, analysis)
        mkey = 'bayes_NP' if analysis == 'NP' else 'bayes_NPSMBHB'
        pkey = 'maxpost_NP' if analysis == 'NP' else 'maxpost_NPSMBHB'
        ckey = 'ci68_NP' if analysis == 'NP' else 'ci68_NPSMBHB'
        rb = rrow[1] if analysis == 'NP' else rrow[2]
        rp = rrow[3] if analysis == 'NP' else rrow[4]
        rc = rrow[5] if analysis == 'NP' else rrow[6]

        if key not in measured:
            if prow[mkey] is not None:
                missing.append((model, analysis))
            continue
        mm = measured[key]['params'].get(param)
        if mm is None or 'error' in (mm or {}):
            if prow[mkey] is not None:
                rows_out.append(dict(model=model, param=param, analysis=analysis,
                                     cell='ALL', printed='', measured='',
                                     verdict='not-checkable',
                                     note=(mm or {}).get('error', 'param absent from chain')))
            continue

        pr = mm.get('prior_range')
        # Bayes estimator: mean
        if prow[mkey] is not None:
            parts = split_pm(rb)
            d = decimals(parts[0])
            delta = mm['mean'] - prow[mkey]['value']
            rows_out.append(dict(model=model, param=param, analysis=analysis,
                                 cell='bayes_mean', printed=prow[mkey]['value'],
                                 measured=round(mm['mean'], 5), delta=round(delta, 5),
                                 dec=d, tol=tol_for(d, 'mean'),
                                 verdict=verdict(delta, tol_for(d, 'mean'), d, 'mean'),
                                 note=''))
            if 'sd' in prow[mkey]:
                dsd = decimals(parts[1]) if len(parts) > 1 else d
                delta = mm['sd_ddof0'] - prow[mkey]['sd']
                rows_out.append(dict(model=model, param=param, analysis=analysis,
                                     cell='bayes_sd', printed=prow[mkey]['sd'],
                                     measured=round(mm['sd_ddof0'], 5), delta=round(delta, 5),
                                     dec=dsd, tol=tol_for(dsd, 'sd'),
                                     verdict=verdict(delta, tol_for(dsd, 'sd'), dsd, 'sd'),
                                     note='ddof1=%.5f' % mm['sd_ddof1']))

        # Maximum posterior
        if prow[pkey] is not None:
            d = decimals(rp)
            best = None
            for tag, dd in mm['density'].items():
                v = dd['maxpost']
                if best is None or abs(v - prow[pkey]['value']) < abs(best[1] - prow[pkey]['value']):
                    best = (tag, v)
            mv = mm['density']['scott']['maxpost']
            delta = mv - prow[pkey]['value']
            vd = verdict(delta, 0.1, d, 'maxpost')
            note = 'best=%s(%.4f)' % (best[0], best[1])
            if prow[pkey].get('boundary') and pr:
                span = pr[1] - pr[0]
                if min(abs(mv - pr[0]), abs(mv - pr[1])) <= 0.02 * abs(span):
                    vd = 'reproduced'
                    note += '; boundary rule'
            rows_out.append(dict(model=model, param=param, analysis=analysis,
                                 cell='maxpost', printed=prow[pkey]['value'],
                                 measured=round(mv, 5), delta=round(delta, 5),
                                 dec=d, tol=0.1, verdict=vd, note=note))

        # 68% credible interval
        if prow[ckey] is not None:
            ci = prow[ckey]
            d = max(decimals(ci['raw'].split(',')[0]), decimals(ci['raw'].split(',')[1]))
            for side, pv, mi in (('lo', ci['lo'], 0), ('hi', ci['hi'], 1)):
                prim = mm['hpd68_shortest'][mi]
                sec = mm['density']['scott']['hpd68_levelset'][mi]
                bestt, bestv = None, None
                for tag, dd in mm['density'].items():
                    v = dd['hpd68_levelset'][mi]
                    if bestv is None or abs(v - pv) < abs(bestv - pv):
                        bestt, bestv = tag, v
                dp = prim - pv
                ds = sec - pv
                # PREREG section 3: the shortest contiguous 68% interval is the
                # PRIMARY estimator and decides the verdict; the level-set interval
                # is the declared secondary, reported alongside.
                rows_out.append(dict(
                    model=model, param=param, analysis=analysis,
                    cell='ci68_' + side, printed=pv,
                    measured=round(prim, 5), delta=round(dp, 5),
                    dec=d, tol=tol_for(d, 'ci'),
                    verdict=verdict(dp, tol_for(d, 'ci'), d, 'ci'),
                    note='levelset_scott=%.4f (d=%+.4f, %s); best_ls=%s(%.4f); pct16/84=%.4f' % (
                        sec, ds, verdict(ds, tol_for(d, 'ci'), d, 'ci'),
                        bestt, bestv, mm['pct_16_84'][mi])))

for r in rows_out:
    r.setdefault('delta', '')
    r.setdefault('dec', '')
    r.setdefault('tol', '')

fields = ['model', 'param', 'analysis', 'cell', 'printed', 'measured', 'delta', 'dec', 'tol', 'verdict', 'note']
with open(os.path.join(HERE, 'out', 'comparison.csv'), 'w', newline='', encoding='utf-8') as f:
    w = csv.DictWriter(f, fieldnames=fields)
    w.writeheader()
    for r in rows_out:
        w.writerow({k: r.get(k, '') for k in fields})

from collections import Counter
print('rows:', len(rows_out))
print('by cell type / verdict:')
cnt = Counter((r['cell'].split('_')[0], r['verdict']) for r in rows_out)
for k in sorted(cnt):
    print('  %-10s %-16s %d' % (k[0], k[1], cnt[k]))
print('overall:', Counter(r['verdict'] for r in rows_out))
if missing:
    print('MISSING measured:', sorted(set(missing)))
