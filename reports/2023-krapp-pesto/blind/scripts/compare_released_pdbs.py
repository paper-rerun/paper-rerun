# Compares my labels and my predictions against the authors' released per-structure files in
# repo/pdbs_test (prediction, _T ground truth, _M MaSIF-site). CC BY-NC-SA 4.0.
import json, os, subprocess, sys
import numpy as np

REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'repo'))
WORK = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'work', 'released'))
os.makedirs(WORK, exist_ok=True)


def git_show(path):
    return subprocess.run(['git', 'cat-file', '-p', 'HEAD:' + path], cwd=REPO,
                          capture_output=True).stdout.decode('utf-8', 'replace')


def ca_bfactors(text):
    out = []
    for line in text.splitlines():
        if line[:4] == 'ATOM' and line[12:15].strip() == 'CA':
            out.append(float(line[60:66]))
    return np.array(out)


def main():
    recs = []
    for l in open('out/masif.jsonl'):
        r = json.loads(l)
        if r.get('sid') and 'note' not in r:
            recs.append(r)
    names = set(subprocess.run(['git', 'ls-tree', '-r', '--name-only', 'HEAD', 'pdbs_test'],
                               cwd=REPO, capture_output=True).stdout.decode().split())
    print('released files:', len(names))
    nmatch_y = nmatch_p = 0
    report = []
    for r in recs:
        pid, ba, cid = r['key'].split('/')
        akey = 'pdbs_test/%s_%s_%s_%s' % (pid[1:3].upper(), pid.upper(), ba, cid)
        f_p, f_t = akey + '.pdb', akey + '_T.pdb'
        if f_t not in names:
            report.append((r['key'], 'no released file', None, None))
            continue
        yt = ca_bfactors(git_show(f_t))
        pp = ca_bfactors(git_show(f_p))
        y = np.array(r['y'], dtype=float)
        p = np.array(r['p'], dtype=float)
        if yt.shape != y.shape:
            report.append((r['key'], 'size %d vs %d' % (yt.shape[0], y.shape[0]), None, None))
            continue
        dy = int(np.sum(yt != y))
        dp = float(np.max(np.abs(np.round(p, 2) - pp)))
        nmatch_y += (dy == 0)
        nmatch_p += (dp <= 0.011)
        report.append((r['key'], 'ok', dy, dp))
    print('entries compared        :', len([x for x in report if x[1] == 'ok']))
    print('identical label vectors :', nmatch_y)
    print('predictions equal to 2dp:', nmatch_p)
    for k, s, dy, dp in report:
        if s != 'ok' or dy or (dp is not None and dp > 0.011):
            print('  %-14s %s  label diffs=%s  max pred diff=%s' % (k, s, dy, dp))


if __name__ == '__main__':
    main()
