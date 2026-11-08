# Medians, intervals and set comparison for the blind PeSTo rerun. CC BY-NC-SA 4.0.
import json, csv, sys, collections
import numpy as np

rng = np.random.default_rng(0)


def boot_ci(v, n=20000):
    v = np.asarray(v, dtype=float)
    b = np.median(rng.choice(v, (n, len(v)), replace=True), axis=1)
    return float(np.median(v)), float(np.percentile(b, 2.5)), float(np.percentile(b, 97.5))


def load(fp):
    out = []
    for l in open(fp):
        try:
            out.append(json.loads(l))
        except Exception:
            pass
    return out


def masif_report():
    recs = [r for r in load('out/masif.jsonl') if r.get('auc') is not None or r.get('note')]
    kept = [r for r in load('out/masif.jsonl') if 'note' not in r and r.get('sid')]
    drop = [r for r in load('out/masif.jsonl') if r.get('note')]
    print('== MaSIF-site benchmark set')
    print('entries kept          :', len(kept))
    print('entries dropped       :', len(drop), [(r['key'], r.get('note'), r.get('n_res'), r.get('n_masif')) for r in drop])
    aucs = [r['auc'] for r in kept if r['auc'] is not None]
    print('AUC defined           :', len(aucs), 'of', len(kept))
    m, lo, hi = boot_ci(aucs)
    print('PeSTo median ROC AUC  : %.4f   bootstrap 95%% [%.4f, %.4f]' % (m, lo, hi))
    print('PeSTo mean            : %.4f' % np.mean(aucs))

    # authors' values
    auth = collections.defaultdict(list)
    for r in csv.DictReader(open('work/fig2b_comparison.csv')):
        auth[r['sid']].append(r)
    mine_by_sid = collections.defaultdict(list)
    for r in kept:
        mine_by_sid[r['sid']].append(r)

    print('\n-- set comparison against Source Data sheet Fig2b-comparison')
    a_sids = collections.Counter(s for s in auth for _ in auth[s])
    m_sids = collections.Counter(r['sid'] for r in kept)
    print('authors: %d entries / %d unique sids' % (sum(a_sids.values()), len(a_sids)))
    print('mine   : %d entries / %d unique sids' % (sum(m_sids.values()), len(m_sids)))
    diff = {k: (a_sids.get(k, 0), m_sids.get(k, 0)) for k in set(a_sids) | set(m_sids)
            if a_sids.get(k, 0) != m_sids.get(k, 0)}
    print('sid multiplicity differences:', diff if diff else 'none')

    print('\n-- per structure, mine vs authors (PeSTo AUC)')
    rows = []
    big = []
    for sid in sorted(m_sids):
        mi = sorted([r['auc'] for r in mine_by_sid[sid] if r['auc'] is not None])
        au = sorted([float(x['PeSTo']) for x in auth.get(sid, [])])
        for i in range(max(len(mi), len(au))):
            a = au[i] if i < len(au) else None
            b = mi[i] if i < len(mi) else None
            d = (b - a) if (a is not None and b is not None) else None
            rows.append((sid, a, b, d))
            if d is not None and abs(d) > 0.005:
                big.append((sid, a, b, d))
    for sid, a, b, d in rows:
        print('  %-9s authors=%s mine=%s delta=%s' % (sid,
              'None' if a is None else '%.3f' % a,
              'None' if b is None else '%.4f' % b,
              'None' if d is None else '%+.4f' % d))
    print('structures off by more than 0.005:', len(big), big)

    # C3: best of four methods, with my PeSTo and the authors' other three
    print('\n-- C3: best method per structure (my PeSTo vs authors MaSIF-site/SPPIDER/PSIVER)')
    n_best = 0
    used = 0
    for sid in sorted(m_sids):
        mi = sorted([r['auc'] for r in mine_by_sid[sid] if r['auc'] is not None])
        au = auth.get(sid, [])
        au_sorted = sorted(au, key=lambda x: float(x['PeSTo']))
        for i in range(min(len(mi), len(au_sorted))):
            used += 1
            others = [float(au_sorted[i][k]) for k in ['MaSIF-site', 'SPPIDER', 'PSIVER']]
            if mi[i] > max(others):
                n_best += 1
    print('PeSTo best on %d of %d structures' % (n_best, used))

    # C4: MaSIF-site AUC against my labels
    print('\n-- C4: MaSIF-site median AUC against MY labels')
    from sklearn.metrics import roc_auc_score
    masif = json.load(open('work/masif_pred_per_res.json'))
    vals = []
    for r in kept:
        y = np.array(r['y'])
        p = np.array(masif[r['sid']], dtype=float)
        if p.shape[0] != y.shape[0]:
            continue
        if 0 < y.sum() < y.shape[0]:
            vals.append(roc_auc_score(y, p))
    m2, lo2, hi2 = boot_ci(vals)
    print('MaSIF-site median = %.4f  n=%d  bootstrap 95%% [%.4f, %.4f]' % (m2, len(vals), lo2, hi2))


def scannet_report():
    recs = [r for r in load('out/scannet.jsonl') if r.get('sid')]
    miss = [r for r in load('out/scannet.jsonl') if not r.get('sid')]
    want = [l.strip() for l in open('work/scannet_sids.txt') if l.strip()]
    print('\n== ScanNet-shared set')
    by_sid = collections.defaultdict(list)
    for r in recs:
        by_sid[r['sid']].append(r)
    print('sids requested        :', len(want))
    print('sids with an entry    :', len(by_sid))
    print('sids with no entry    :', len([s for s in want if s not in by_sid]))
    print('no biounit file       :', [r['key'] for r in miss])
    print('sids needing ba > 1   :', len([s for s in by_sid if min(r['ba'] for r in by_sid[s]) > 1]))
    print('sids with >1 entry in the chosen assembly:',
          len([s for s in by_sid if len(by_sid[s]) > 1]))
    chosen = []
    for s in sorted(by_sid):
        rs = sorted(by_sid[s], key=lambda r: (r['ba'], r['cid']))
        chosen.append(rs[0])
    aucs = [r['auc'] for r in chosen if r['auc'] is not None]
    print('AUC defined           :', len(aucs), 'of', len(chosen))
    m, lo, hi = boot_ci(aucs)
    print('PeSTo median ROC AUC  : %.4f   bootstrap 95%% [%.4f, %.4f]' % (m, lo, hi))
    print('PeSTo mean            : %.4f' % np.mean(aucs))
    auth = {r['sid']: r for r in csv.DictReader(open('work/fig2b_scannet.csv'))}
    d = []
    for r in chosen:
        if r['auc'] is None or r['sid'] not in auth:
            continue
        d.append((r['sid'], float(auth[r['sid']]['PeSTo_auc']), r['auc']))
    delta = np.array([x[2] - x[1] for x in d])
    print('paired with authors   :', len(d))
    print('|delta| <= 0.005      : %d (%.1f%%)' % (int(np.sum(np.abs(delta) <= 0.005)),
                                                   100 * np.mean(np.abs(delta) <= 0.005)))
    print('median |delta|        : %.5f ; max |delta| : %.4f' % (np.median(np.abs(delta)), np.max(np.abs(delta))))
    worst = sorted(d, key=lambda x: -abs(x[2] - x[1]))[:15]
    for sid, a, b in worst:
        print('  %-9s authors=%.4f mine=%.4f delta=%+.4f' % (sid, a, b, b - a))
    # restrict the median to the sids both have
    sub = [x[2] for x in d]
    m3, lo3, hi3 = boot_ci(sub)
    print('median on the paired subset: %.4f [%.4f, %.4f]' % (m3, lo3, hi3))
    t = [r['t'] for r in chosen if r.get('t')]
    print('inference time per structure: mean %.1f s, median %.1f s, max %.1f s' % (np.mean(t), np.median(t), np.max(t)))


if __name__ == '__main__':
    which = sys.argv[1] if len(sys.argv) > 1 else 'both'
    if which in ('masif', 'both'):
        masif_report()
    if which in ('scannet', 'both'):
        scannet_report()
