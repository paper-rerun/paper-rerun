import sys, math, io
from fractions import Fraction as F
out=io.StringIO()
def p(*a): print(*a,file=out)
rows=[(1024,0.9809523810,0.1335032930),(2048,0.9466666667,0.2196967607),
      (4096,0.9475000000,0.2129994131),(8192,0.8036324786,0.3649624567),
      (16384,0.5357914308,0.3412057061),(32768,0.1300426936,0.1135178150)]
def stats(vals):
    n=len(vals); m=sum(vals)/n
    var=sum((v-m)**2 for v in vals)/n
    return float(m), math.sqrt(float(var))
p("Candidate reconstructions. Each F1 section score the released code can emit is")
p("0 or 2/(2+fp). A 100-section population is tried; the two rows below sit exactly")
p("at the maximum dispersion a 100-value sample with that mean can have.")
for noise,m,s in rows:
    tot=m*100
    k=int(math.floor(tot+1e-9)); rem=F(round((tot-k)*1e9),10**9).limit_denominator(1000)
    vals=[F(1)]*k+[rem]+[F(0)]*(100-k-1)
    mm,ss=stats(vals)
    hit = abs(mm-m)<2e-9 and abs(ss-s)<2e-7
    p(f"noise {noise:>6}: published mean {m:.10f} sd {s:.10f}")
    p(f"   trial 100-value config: {k} x 1 + 1 x {rem} + {100-k-1} x 0")
    p(f"   -> mean {mm:.10f} sd {ss:.10f}   {'EXACT MATCH' if hit else 'no match (mean ok: %s)'%(abs(mm-m)<2e-9)}")
    for N in (10,100):
        ci=1.96*s/math.sqrt(N)
        p(f"   95% CI half-width with N={N}: {ci:.4f}  -> mean+CI = {m+ci:.4f}")
open(sys.argv[1],'w',encoding='utf-8').write(out.getvalue())
