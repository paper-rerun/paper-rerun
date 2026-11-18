import zipfile,tarfile,io,numpy as np
z=zipfile.ZipFile(r"E:\Ciencia\noturno\2023-antoniadis-epta-dr2\data\chains.zip")
t=tarfile.open(fileobj=io.BytesIO(z.read("chains/DR2new/hd_pl.tar.gz")),mode="r:gz")
n=[m.name for m in t.getmembers() if m.isfile()]
pars=[l.strip() for l in t.extractfile([x for x in n if x.endswith("pars.txt")][0]).read().decode().splitlines() if l.strip()]
raw=t.extractfile([x for x in n if x.endswith("chain_1.txt")][0]).read().decode()
arr=np.array([[float(v) for v in l.split()] for l in raw.splitlines() if l.strip()])
g=arr[:,pars.index("gw_hd_gamma")]
print("thinning scan, C2 gamma lower bound (paper prints 0.71 -> admissible 0.705..0.715)")
for k in range(1,21):
    vals=[]
    for ph in range(k):
        s=g[ph::k]; s=s[len(s)//4:]
        vals.append(float(np.median(s)-np.percentile(s,5)))
    hit=sum(1 for v in vals if 0.705<=v<=0.715)
    print("  k=%2d n=%5d  min %.4f  max %.4f  phases inside the printed value: %d/%d"%(k,len(g[::k])-len(g[::k])//4,min(vals),max(vals),hit,k))
