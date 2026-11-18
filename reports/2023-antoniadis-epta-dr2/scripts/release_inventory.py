import zipfile, tarfile, io
import numpy as np
import os
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
z = zipfile.ZipFile(r"E:\Ciencia\noturno\2023-antoniadis-epta-dr2\data\chains.zip")
L=[]
def peek(member):
    t = tarfile.open(fileobj=io.BytesIO(z.read(member)), mode="r:gz")
    names = t.getnames(); pars=None; n=None
    for nm in names:
        if nm.endswith("pars.txt"): pars = t.extractfile(nm).read().decode().split()
        if nm.endswith("chain_1.txt"): n = sum(1 for _ in t.extractfile(nm))
    t.close(); return names, pars, n
for m in ["chains/DR2full/os.tar.gz","chains/DR2new/crn_fs.tar.gz","chains/DR2full/crn_fs.tar.gz",
          "chains/DR2new+/hd_pl.tar.gz","chains/DR2full+/hd_pl.tar.gz","chains/DR2full/hd_pl.tar.gz"]:
    names,pars,n = peek(m)
    rho = len([p for p in (pars or []) if "log10_rho" in p])
    L.append("%-28s arquivos=%s  pars=%s  rho=%d  linhas=%s" % (m, [x.split('/')[-1] for x in names if '/' in x][:4], len(pars) if pars else None, rho, n))
# B3: diferenca entre DR2full e DR2full+ no hd_pl
_,pf,_ = peek("chains/DR2full/hd_pl.tar.gz")
_,pp,_ = peek("chains/DR2full+/hd_pl.tar.gz")
L.append("")
L.append("B3: hd_pl DR2full tem %d params, DR2full+ tem %d" % (len(pf), len(pp)))
L.append("   so em DR2full : %s" % sorted(set(pf)-set(pp)))
L.append("   so em DR2full+: %s" % sorted(set(pp)-set(pf)))
txt="\n".join(L)+"\n"
io.open(os.path.join(ROOT, "runs", "logs", "release_inventory.log"), "w",encoding="utf-8",newline="\n").write(txt)
print(txt)
