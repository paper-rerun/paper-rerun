import json, subprocess, os
import numpy as np
REPO=os.path.abspath('repo')
def git_show(p):
    return subprocess.run(['git','cat-file','-p','HEAD:'+p],cwd=REPO,capture_output=True).stdout.decode()
def ca(t,lo,hi):
    return np.array([float(l[lo:hi]) for l in t.splitlines() if l[:4]=='ATOM' and l[12:15].strip()=='CA'])
masif=json.load(open('work/masif_pred_per_res.json'))
n=0; bad=0
for l in open('out/masif.jsonl'):
    r=json.loads(l)
    if not r.get('sid') or 'note' in r: continue
    pid,ba,cid=r['key'].split('/')
    base='pdbs_test/%s_%s_%s_%s'%(pid[1:3].upper(),pid.upper(),ba,cid)
    t=git_show(base+'_M.pdb')
    if not t: continue
    v=ca(t,60,66); ref=np.array(masif[r['sid']],dtype=float)
    n+=1
    d=np.max(np.abs(np.round(ref,2)-v)) if v.shape==ref.shape else -1
    if d>0.011 or d<0: bad+=1; print(r['key'],'maxdiff',d, v.shape, ref.shape)
print('compared',n,'mismatching',bad)
