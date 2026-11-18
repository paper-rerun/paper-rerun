"""Independent recount from chains.zip, read in memory. No reuse of the run's code."""
import zipfile, tarfile, io, json, sys
import numpy as np

ZIP = r"E:\Ciencia\noturno\2023-antoniadis-epta-dr2\data\chains.zip"

def quantile_t7(sorted_x, p):
    """R type-7 / numpy 'linear', written out by hand."""
    n = len(sorted_x)
    h = (n - 1) * p
    lo = int(np.floor(h)); hi = min(lo + 1, n - 1)
    return sorted_x[lo] + (h - lo) * (sorted_x[hi] - sorted_x[lo])

def load(member):
    z = zipfile.ZipFile(ZIP)
    t = tarfile.open(fileobj=io.BytesIO(z.read(member)), mode="r:gz")
    names = [m.name for m in t.getmembers() if m.isfile()]
    pars = [l.strip() for l in t.extractfile([n for n in names if n.endswith("pars.txt")][0]).read().decode().splitlines() if l.strip()]
    raw = t.extractfile([n for n in names if n.endswith("chain_1.txt")][0]).read().decode()
    arr = np.array([[float(v) for v in line.split()] for line in raw.splitlines() if line.strip()])
    return pars, arr

TARGETS = {  # from the ar5iv table, (med, minus, plus)
 ("DR2full","hd_pl","log10_A"): (-14.54,0.41,0.28),
 ("DR2full","hd_pl","gamma"):   (4.19,0.63,0.73),
 ("DR2new","hd_pl","log10_A"):  (-13.94,0.48,0.23),
 ("DR2new","hd_pl","gamma"):    (2.71,0.71,1.18),
 ("DR2full","crn_pl","log10_A"):(-14.53,0.44,0.29),
 ("DR2full","crn_pl","gamma"):  (4.13,0.59,0.80),
 ("DR2new","crn_pl","log10_A"): (-14.00,0.77,0.28),
 ("DR2new","crn_pl","gamma"):   (2.91,0.87,1.72),
 ("DR2full","bin_b10_orf","log10_A"):(-14.47,0.35,0.27),
 ("DR2full","bin_b10_orf","gamma"):  (4.10,0.56,0.64),
 ("DR2new","bin_b10_orf","log10_A"): (-13.89,0.32,0.22),
 ("DR2new","bin_b10_orf","gamma"):   (2.63,0.71,0.86),
 ("DR2full","chebyshev_orf","log10_A"):(-14.50,0.40,0.32),
 ("DR2full","chebyshev_orf","gamma"):  (4.17,0.72,0.73),
 ("DR2new","chebyshev_orf","log10_A"): (-13.87,0.31,0.22),
 ("DR2new","chebyshev_orf","gamma"):   (2.57,0.76,0.86),
 ("DR2full","legendre_orf","log10_A"):(-14.51,0.40,0.30),
 ("DR2full","legendre_orf","gamma"):  (4.19,0.63,0.74),
 ("DR2new","legendre_orf","log10_A"): (-13.89,0.35,0.23),
 ("DR2new","legendre_orf","gamma"):   (2.59,0.72,0.98),
}
PREFIX = {"hd_pl":"gw_hd","crn_pl":"gw_crn","bin_b10_orf":"gw_bin_orf",
          "chebyshev_orf":"gw_chebyshev_orf","legendre_orf":"gw_legendre_orf"}

sets = sys.argv[1].split(",") if len(sys.argv)>1 else ["DR2full","DR2new"]
models = sys.argv[2].split(",") if len(sys.argv)>2 else ["hd_pl","crn_pl"]
out={}
for ds in sets:
    for model in models:
        pars, arr = load("chains/%s/%s.tar.gz" % (ds, model))
        n = arr.shape[0]; burn = n//4
        print("%s/%s  n=%d pars=%d cols=%d" % (ds,model,n,len(pars),arr.shape[1]))
        base = ds.rstrip("+")
        for short in ("log10_A","gamma"):
            name = PREFIX[model]+"_"+short
            assert pars.count(name)==1, (name, pars.count(name))
            x = np.sort(arr[burn:, pars.index(name)])
            med = quantile_t7(x,0.5); p5=quantile_t7(x,0.05); p95=quantile_t7(x,0.95)
            key=(base,model,short)
            t = TARGETS.get(key)
            line = "   %-8s med %+.4f  +%.4f -%.4f" % (short, med, p95-med, med-p5)
            if t and not ds.endswith("+"):
                line += "   | paper %+.2f +%.2f -%.2f  d(med)%+.4f d(+)%+.4f d(-)%+.4f" % (
                    t[0],t[2],t[1], med-t[0], (p95-med)-t[2], (med-p5)-t[1])
            elif t:
                line += "   | paper(EPTA-only row) d(med)%+.4f d(+)%+.4f d(-)%+.4f" % (
                    med-t[0], (p95-med)-t[2], (med-p5)-t[1])
            print(line)
            out["%s/%s/%s"%(ds,model,short)]={"median":med,"p5":p5,"p95":p95,"n":int(n-burn)}
json.dump(out, open("recount_indep_%s.json"%("_".join(sets+models)),"w"), indent=1)
