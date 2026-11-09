import numpy as np
R="/mnt/e/Ciencia/noturno/2024-desi-bao-vi/data/official/"
def load(d, n):
    cols=open(f"{R}{d}/chain.1.txt").readline().lstrip("#").split()
    a=np.vstack([np.loadtxt(f"{R}{d}/chain.{i}.txt") for i in n])
    return cols,a
for d,n in (("desi-bao-all_schoneberg2024-bbn",(1,2,3,4)),("sibling-fixed-nnu",(1,2))):
    cols,a=load(d,n)
    w=a[:,0]; ob=a[:,cols.index("ombh2")]; c=a[:,cols.index("chi2__bbn")]
    p=np.polyfit(ob,c,2); mu=-p[1]/(2*p[0]); sig=1/np.sqrt(p[0])
    res=c-np.polyval(p,ob)
    H=a[:,cols.index("H0")]
    m=np.average(H,weights=w); s=np.sqrt(np.average((H-m)**2,weights=w))
    mb=np.average(ob,weights=w); sb=np.sqrt(np.average((ob-mb)**2,weights=w))
    # constant term: does chi2 at mu = 0 ? (normalisation)
    print(d, "fit mu=%.7f sig=%.7f rms=%.2e chi2_at_mu=%.4f | H0 %.5f +/- %.5f | ombh2 %.6f +/- %.6f | rows %d"%(mu,sig,res.std(),np.polyval(p,mu),m,s,mb,sb,len(a)))
    # burn-in sensitivity: drop first 30% of each chain
# conditional of the 2D Gaussian in chain.updated.yaml at nnu=3.044
mu=np.array([0.02196,3.034]); C=np.array([[4.0311226e-07,7.30390042e-05],[7.30390042e-05,0.0452831584]])
cm=mu[0]+C[0,1]/C[1,1]*(3.044-mu[1]); cs=np.sqrt(C[0,0]-C[0,1]**2/C[1,1])
print("conditional at Neff=3.044: %.7f +/- %.7f ; marginal %.6f +/- %.6f ; rho %.4f"%(cm,cs,mu[0],np.sqrt(C[0,0]),C[0,1]/np.sqrt(C[0,0]*C[1,1])))
