# Conditional log10A posterior at gamma = 13/3, by slicing the power-law chain.
import numpy as np, json, sys

def load(d):
    pars=[l.strip() for l in open(f"{d}/pars.txt") if l.strip()]
    x=np.loadtxt(f"{d}/chain_1.txt")
    b=int(0.25*len(x)); x=x[b:]
    ig=[i for i,p in enumerate(pars) if p.endswith("_gamma") and p.startswith("gw_")][0]
    ia=[i for i,p in enumerate(pars) if p.endswith("_log10_A") and p.startswith("gw_")][0]
    return x[:,ig], x[:,ia]

def q(a):
    m=np.median(a); lo,hi=np.percentile(a,[5,95])
    return dict(n=len(a), median=round(float(m),4), minus=round(float(m-lo),4), plus=round(float(hi-m),4),
                A_e15=round(float(10**m/1e-15),3), A_lo=round(float(10**lo/1e-15),3), A_hi=round(float(10**hi/1e-15),3))

out={}
g13=13/3
for name,d in [("DR2full_hd","extracted/chains/DR2full/hd_pl/hd_pl"),
               ("DR2new_hd","extracted/chains/DR2new/hd_pl/hd_pl"),
               ("DR2full_crn","extracted/chains/DR2full/crn_pl/crn_pl"),
               ("DR2new_crn","extracted/chains/DR2new/crn_pl/crn_pl")]:
    g,a=load(d)
    out[name]={}
    for dg in (0.02,0.05,0.1,0.2,0.3):
        sel=np.abs(g-g13)<dg
        if sel.sum()>30:
            out[name][f"|dg|<{dg}"]=q(a[sel])
# both HD data sets pooled
gf,af=load("extracted/chains/DR2full/hd_pl/hd_pl")
gn,an=load("extracted/chains/DR2new/hd_pl/hd_pl")
for dg in (0.05,0.1,0.2):
    sel=np.concatenate([af[np.abs(gf-g13)<dg], an[np.abs(gn-g13)<dg]])
    out.setdefault("pooled_hd",{})[f"|dg|<{dg}"]=q(sel)
open("out/slice13over3.json","w",encoding="utf-8").write(json.dumps(out,indent=1))
