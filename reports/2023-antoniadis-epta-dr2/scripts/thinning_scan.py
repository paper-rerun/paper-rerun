import io, numpy as np
import os
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
d = r"E:\Ciencia\noturno\2023-antoniadis-epta-dr2\data\extracted\DR2new__hd_pl\hd_pl"
pars = [l.strip() for l in io.open(d + r"\pars.txt") if l.strip()]
arr = np.loadtxt(d + r"\chain_1.txt")
x_all = arr[:, pars.index("gw_hd_gamma")]
x = x_all[len(x_all)//4:]
L = []
L.append("B1: thinning, burn-in de 25%% primeiro, depois pega 1 a cada k")
for k in (1,2,3,4,5,6,8,10,12,15,20):
    phases = []
    for off in range(k):
        y = x[off::k]
        m = np.median(y); p5 = np.percentile(y,5)
        phases.append(m-p5)
    inside = sum(1 for v in phases if 0.705 <= v < 0.715)
    L.append("  k=%2d  fase0 %.4f  min %.4f  max %.4f  fases dentro de [0.705,0.715): %d de %d"
             % (k, phases[0], min(phases), max(phases), inside, k))
L.append("")
L.append("B2: aritmetica da distancia ate a faixa de arredondamento")
med = np.median(x); p5 = np.percentile(x,5); ours = med-p5
L.append("  nossa borda %.4f ; impresso 0.71 -> verdadeiro em [0.705, 0.715)" % ours)
L.append("  distancia ate 0.715 = %.4f" % (ours-0.715))
L.append("  distancia ate 0.71  = %.4f" % (ours-0.71))
txt = "\n".join(L)+"\n"
io.open(os.path.join(ROOT, "runs", "logs", "thinning_scan.log"), "w",encoding="utf-8",newline="\n").write(txt)
print(txt)
