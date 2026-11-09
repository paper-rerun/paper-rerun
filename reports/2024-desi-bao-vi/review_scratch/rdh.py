import numpy as np
D="/mnt/e/Ciencia/noturno/2024-desi-bao-vi/data/official/desi-bao-all"
cols=open(f"{D}/chain.1.txt").readline().lstrip("#").split()
rows=[np.loadtxt(f"{D}/chain.{i}.txt") for i in (1,2,3,4)]
def wq(x,w,q):
    o=np.argsort(x); c=np.cumsum(w[o]); c/=c[-1]; return np.interp(q,c,x[o])
for burn in (0.0,0.3,0.5):
    d=np.vstack([r[int(burn*len(r)):] for r in rows]); w=d[:,0]
    for name in ("hrdrag","omm"):
        x=d[:,cols.index(name)]; m=np.average(x,weights=w); s=np.sqrt(np.average((x-m)**2,weights=w))
        lo,med,hi=wq(x,w,[0.15865,0.5,0.84135])
        h,e=np.histogram(x,bins=80,weights=w); pk=0.5*(e[h.argmax()]+e[h.argmax()+1])
        print("burn %.1f %-7s mean %.4f sd %.4f median %.4f 68%% [%.4f, %.4f] peak~%.3f"%(burn,name,m,s,med,lo,hi,pk))
    # per-chain means
    print("  per-chain hrdrag means:", [round(float(np.average(r[int(burn*len(r)):,cols.index('hrdrag')],weights=r[int(burn*len(r)):,0])),3) for r in rows])
