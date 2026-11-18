import zipfile,tarfile,io
import numpy as np
z=zipfile.ZipFile(r"E:\Ciencia\noturno\2023-antoniadis-epta-dr2\data\chains.zip")
def load(ds,model):
    t=tarfile.open(fileobj=io.BytesIO(z.read("chains/%s/%s.tar.gz"%(ds,model))),mode="r:gz")
    n=[m.name for m in t.getmembers() if m.isfile()]
    pars=[l.strip() for l in t.extractfile([x for x in n if x.endswith("pars.txt")][0]).read().decode().splitlines() if l.strip()]
    raw=t.extractfile([x for x in n if x.endswith("chain_1.txt")][0]).read().decode()
    return pars,np.array([[float(v) for v in l.split()] for l in raw.splitlines() if l.strip()])
def kde_q(x,qs):
    # Silverman bandwidth gaussian KDE -> CDF on a grid
    n=len(x); h=1.06*x.std(ddof=1)*n**-0.2
    grid=np.linspace(x.min()-3*h,x.max()+3*h,4000)
    from math import erf
    # CDF = mean of Phi((grid-xi)/h)
    xs=np.sort(x)
    cdf=np.array([0.5*(1+np.vectorize(erf)((g-xs)/(h*np.sqrt(2)))).mean() for g in grid])
    return np.interp(qs,cdf,grid)
CASES=[("DR2full","hd_pl","gw_hd",(-14.54,.41,.28),(4.19,.63,.73)),
       ("DR2new","hd_pl","gw_hd",(-13.94,.48,.23),(2.71,.71,1.18)),
       ("DR2full","crn_pl","gw_crn",(-14.53,.44,.29),(4.13,.59,.80))]
tot_e=tot_k=0
for ds,model,pre,tA,tG in CASES:
    pars,arr=load(ds,model); burn=arr.shape[0]//4
    for short,t in (("log10_A",tA),("gamma",tG)):
        x=arr[burn:,pars.index(pre+"_"+short)]
        p5,med,p95=np.percentile(x,[5,50,95])
        k5,kmed,k95=kde_q(x,[0.05,0.5,0.95])
        e=(abs((p95-med)-t[2])+abs((med-p5)-t[1])); k=(abs((k95-kmed)-t[2])+abs((kmed-k5)-t[1]))
        tot_e+=e; tot_k+=k
        print("%s %s %-8s paper +%.2f -%.2f | perc +%.4f -%.4f | KDE +%.4f -%.4f"%(ds,model,short,t[2],t[1],p95-med,med-p5,k95-kmed,kmed-k5))
print("soma erro abs bordas: percentil %.4f  KDE %.4f"%(tot_e,tot_k))
