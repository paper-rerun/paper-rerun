import json, csv, collections
import numpy as np
recs=[json.loads(l) for l in open('out/scannet.jsonl')]
recs=[r for r in recs if r.get('sid')]
want=[l.strip() for l in open('work/scannet_sids.txt') if l.strip()]
by=collections.defaultdict(list)
for r in recs: by[r['sid']].append(r)
print('missing sid:', [s for s in want if s not in by])
auth={r['sid']:r for r in csv.DictReader(open('work/fig2b_scannet.csv'))}
print('\n4DX0_A all entries:')
for r in sorted(by.get('4DX0_A',[]), key=lambda r:(r['ba'],r['cid'])):
    print('  ', {k:r[k] for k in ['key','ba','cid','n_res','n_atoms','n_pos','n_raw','n_subunits','auc']})
print('   authors auc', auth['4DX0_A']['PeSTo_auc'], 'tpr', auth['4DX0_A']['PeSTo_tpr'], 'time', auth['4DX0_A']['time'])
# for the multi-entry sids, does any sibling match the authors better than the chosen one?
better=0; tot=0
for s,rs in by.items():
    if len(rs)<2 or s not in auth: continue
    tot+=1
    a=float(auth[s]['PeSTo_auc'])
    rs2=sorted(rs,key=lambda r:(r['ba'],r['cid']))
    d0=abs(rs2[0]['auc']-a)
    dbest=min(abs(r['auc']-a) for r in rs2)
    if dbest < d0 - 1e-6: better+=1
print(f'\nsids with several entries: {tot}; a sibling would match the authors better in {better}')
