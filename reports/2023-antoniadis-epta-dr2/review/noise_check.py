"""Independent ESS + subsample experiment for C2 gamma (DR2new hd_pl)."""
import zipfile, tarfile, io
import numpy as np
z=zipfile.ZipFile(r"E:\Ciencia\noturno\2023-antoniadis-epta-dr2\data\chains.zip")
def load(ds,model):
    t=tarfile.open(fileobj=io.BytesIO(z.read("chains/%s/%s.tar.gz"%(ds,model))),mode="r:gz")
    names=[m.name for m in t.getmembers() if m.isfile()]
    pars=[l.strip() for l in t.extractfile([n for n in names if n.endswith("pars.txt")][0]).read().decode().splitlines() if l.strip()]
    raw=t.extractfile([n for n in names if n.endswith("chain_1.txt")][0]).read().decode()
    arr=np.array([[float(v) for v in l.split()] for l in raw.splitlines() if l.strip()])
    return pars,arr

def tau_ips(x):
    """Initial positive sequence (Geyer) estimator - different from Sokal windowing."""
    x=x-x.mean(); n=len(x)
    f=np.fft.rfft(x,2*n); acf=np.fft.irfft(f*np.conj(f))[:n].real; acf/=acf[0]
    # pair sums Gamma_k = rho_2k + rho_2k+1, truncate at first negative
    s=0.0
    for k in range(0,n//2-1):
        g=acf[2*k]+acf[2*k+1]
        if g<0: break
        s+=g
    return 2*s-1.0

def tau_batch(x, nb=50):
    n=len(x); m=n//nb
    means=np.array([x[i*m:(i+1)*m].mean() for i in range(nb)])
    return m*means.var(ddof=1)/x.var(ddof=1)

for ds,model,prefix in (("DR2full","hd_pl","gw_hd"),("DR2new","hd_pl","gw_hd"),("DR2full","crn_pl","gw_crn")):
    pars,arr=load(ds,model); burn=arr.shape[0]//4
    for short in ("log10_A","gamma"):
        x=arr[burn:,pars.index(prefix+"_"+short)]
        t1,t2=tau_ips(x),tau_batch(x)
        print("%s %s %-8s  tau_geyer %.1f (ESS %.0f)   tau_batch50 %.1f (ESS %.0f)"%(ds,model,short,t1,len(x)/t1,t2,len(x)/t2))

# --- subsample experiment on C2 gamma
pars,arr=load("DR2new","hd_pl")
g=arr[:,pars.index("gw_hd_gamma")]
med_full=np.median(g[len(g)//4:]); 
print("\nC2 gamma: paper prints med 2.71 minus 0.71 -> p5 in [1.990, 2.010] after rounding")
print("ours p5 = %.4f  (minus %.4f)"%(np.percentile(g[len(g)//4:],5), med_full-np.percentile(g[len(g)//4:],5)))
rng=np.random.default_rng(7)
# thinning by k, all phases
print("\nthinning:")
for k in (2,3,4,5,10):
    vals=[]
    for ph in range(k):
        s=g[ph::k]; s=s[len(s)//4:]
        vals.append(np.median(s)-np.percentile(s,5))
    print("   k=%2d  minus from %.4f to %.4f"%(k,min(vals),max(vals)))
# contiguous windows of 22493
print("\ncontiguous windows of 22493 samples (step 500):")
w=22493; vals=[]
for st in range(0,len(g)-w+1,500):
    s=g[st:st+w]; vals.append(np.median(s)-np.percentile(s,5))
vals=np.array(vals)
print("   minus from %.4f to %.4f ; fraction <=0.715: %.2f"%(vals.min(),vals.max(),(vals<=0.715).mean()))
# moving block bootstrap of the 'minus' statistic itself
def mbb(x,block,nboot=2000):
    n=len(x); nb=int(np.ceil(n/block)); out=np.empty(nboot); idx=np.arange(block)
    st=rng.integers(0,n-block,size=(nboot,nb))
    for i in range(nboot):
        s=(st[i][:,None]+idx[None,:]).ravel()[:n]; y=x[s]
        out[i]=np.median(y)-np.percentile(y,5)
    return out
x=g[len(g)//4:]
b=mbb(x,109)
print("\nMBB on the 'minus' statistic (block 109): sd %.4f ; P(minus<=0.715) = %.3f ; P(<=0.71)=%.3f"%(b.std(ddof=1),(b<=0.715).mean(),(b<=0.71).mean()))
