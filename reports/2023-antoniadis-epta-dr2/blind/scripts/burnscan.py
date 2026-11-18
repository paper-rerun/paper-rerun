import numpy as np, json
d="extracted/chains/DR2new/hd_pl/hd_pl"
pars=[l.strip() for l in open(f"{d}/pars.txt") if l.strip()]
x=np.loadtxt(f"{d}/chain_1.txt")
ig=pars.index("gw_hd_gamma"); ia=pars.index("gw_hd_log10_A")
rows=[]
for bf in (0.0,0.05,0.1,0.15,0.2,0.25,0.3,0.4,0.5,0.6,0.7):
    b=int(bf*len(x)); g=x[b:,ig]; a=x[b:,ia]
    mg=np.median(g); lg,hg=np.percentile(g,[5,95])
    ma=np.median(a); la,ha=np.percentile(a,[5,95])
    rows.append(f"burn={bf:<5} n={len(g):<6} gamma={mg:.3f} -{mg-lg:.3f} +{hg-mg:.3f}   log10A={ma:.3f} -{ma-la:.3f} +{ha-ma:.3f}")
# bootstrap the 5th percentile of gamma to get its sampling error (block bootstrap, 200 blocks)
b=int(0.25*len(x)); g=x[b:,ig]
nb=200; bl=len(g)//nb
rng=np.random.default_rng(0); vals=[]
for _ in range(400):
    idx=rng.integers(0,nb,nb)
    s=np.concatenate([g[i*bl:(i+1)*bl] for i in idx])
    vals.append(np.median(s)-np.percentile(s,5))
rows.append(f"block-bootstrap of (median - q05) for gamma: mean={np.mean(vals):.3f} sd={np.std(vals):.3f} 5-95%={np.percentile(vals,5):.3f}-{np.percentile(vals,95):.3f}")
open("out/burnscan_DR2new_hd.txt","w",encoding="utf-8").write("\n".join(rows)+"\n")
