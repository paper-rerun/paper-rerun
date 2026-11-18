import json, glob, os
paper = {
 ("DR2full","hd_pl"):  {"log10A": (-14.54,0.41,0.28), "gamma": (4.19,0.63,0.73)},
 ("DR2new","hd_pl"):   {"log10A": (-13.94,0.48,0.23), "gamma": (2.71,0.71,1.18)},
 ("DR2full","crn_pl"): {"log10A": (-14.53,0.44,0.29), "gamma": (4.13,0.59,0.80)},
 ("DR2new","crn_pl"):  {"log10A": (-14.00,0.77,0.28), "gamma": (2.91,0.87,1.72)},
}
rows=[]
for bf in ("0.0","0.25"):
    for (ds,mod),pv in paper.items():
        d=json.load(open(f"out/{ds}_{mod}_burn{bf}.json"))
        for pname,s in d["params"].items():
            key = "log10A" if "log10_A" in pname else "gamma"
            pc,pm,pp = pv[key]
            rows.append((bf,ds,mod,key,
                round(s["median"],3), round(s["median_minus"],3), round(s["median_plus"],3),
                pc,pm,pp,
                round(s["median"]-pc,3), round(s["median_minus"]-pm,3), round(s["median_plus"]-pp,3),
                round(s["mode_hist100"],3), round(s["mode_hpd_minus"],3), round(s["mode_hpd_plus"],3)))
hdr=("burn","data","model","par","mine_med","m-","m+","paper","p-","p+","dmed","d-","d+","mode","hpd-","hpd+")
w=[max(len(str(r[i])) for r in rows+[hdr]) for i in range(len(hdr))]
lines=[" ".join(str(h).ljust(w[i]) for i,h in enumerate(hdr))]
for r in rows:
    lines.append(" ".join(str(c).ljust(w[i]) for i,c in enumerate(r)))
open("out/comparison.txt","w",encoding="utf-8").write("\n".join(lines)+"\n")
