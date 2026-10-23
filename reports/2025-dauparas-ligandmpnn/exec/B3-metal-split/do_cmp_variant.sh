#!/usr/bin/env bash
set -euo pipefail
ROOT=/mnt/e/Ciencia/pipeline/2025-dauparas-ligandmpnn
source "$ROOT/env/activate.sh"
python - "$@" <<'PY'
import csv, json, sys, numpy as np
ROOT='/mnt/e/Ciencia/pipeline/2025-dauparas-ligandmpnn'; EXEC=ROOT+'/exec/B3-metal-split'
flavor, ctx = sys.argv[1], sys.argv[2]
ids=json.load(open(ROOT+'/repo/training/test_metal.json'))
auth={}
for r in csv.DictReader(open(ROOT+'/sources/sd/x/s2/fig_2_3_1.csv')):
    auth.setdefault(r['types'],[]).append(float(r['probs']))
v=json.load(open('%s/variant_%s_%s.json'%(EXEC,flavor,ctx)))
for tag,key in (('lmpnn','LigandMPNN'),('pmpnn','ProteinMPNN')):
    a=np.array(v[tag]['per_protein'],dtype=float); b=np.array(auth[key])
    ok=~np.isnan(a)
    print('%s %s/%s median=%.3f author=%.3f r=%.3f mean|d|=%.2f exact<=1pp=%d/83'%(
        tag,flavor,ctx,np.median(a[ok]),np.median(b),np.corrcoef(a[ok],b[ok])[0,1],
        np.mean(np.abs(a[ok]-b[ok])), int((np.abs(a[ok]-b[ok])<=1).sum())))
PY
