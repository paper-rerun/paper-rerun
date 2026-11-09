import numpy as np, camb
D="/mnt/e/Ciencia/noturno/2024-desi-bao-vi/data/official/desi-bao-all"
DATA="/mnt/e/Ciencia/noturno/2024-desi-bao-vi/data/bao_data"
C_KMS=299792.458; H0F,OBF=67.36,0.02237
cols=open(f"{D}/chain.1.txt").readline().lstrip("#").split()
d=np.vstack([np.loadtxt(f"{D}/chain.{i}.txt") for i in (1,2,3,4)])
z,val,kind=[],[],[]
for line in open(f"{DATA}/desi_2024_gaussian_bao_ALL_GCcomb_mean.txt"):
    if line.startswith("#") or not line.strip(): continue
    a,b,c=line.split(); z.append(float(a)); val.append(float(b)); kind.append(c)
z=np.array(z); val=np.array(val); cov=np.loadtxt(f"{DATA}/desi_2024_gaussian_bao_ALL_GCcomb_cov.txt"); ic=np.linalg.inv(cov)
zu=np.array(sorted(set(z)))
def th(omm,hr):
    h=H0F/100
    p=camb.set_params(H0=H0F,ombh2=OBF,omch2=omm*h*h-0.06/93.14-OBF,mnu=0.06,nnu=3.044,omk=0,TCMB=2.7255,num_massive_neutrinos=1,dark_energy_model="ppf")
    r=camb.get_background(p)
    dm=r.comoving_radial_distance(zu)*h/hr; dh=C_KMS*h/r.hubble_parameter(zu)/hr; dv=(zu*dm**2*dh)**(1/3)
    t={}
    for i,zz in enumerate(zu): t[(zz,"DM_over_rs")]=dm[i]; t[(zz,"DH_over_rs")]=dh[i]; t[(zz,"DV_over_rs")]=dv[i]
    return np.array([t[(zz,k)] for zz,k in zip(z,kind)])
rng=np.random.default_rng(7); pick=rng.choice(len(d),600,replace=False)
T=[]; theirs=d[pick,cols.index("chi2__BAO")]
for i in pick: T.append(th(d[i,cols.index("omm")],d[i,cols.index("hrdrag")]))
T=np.array(T); R=val-T
ours=np.einsum("ni,ij,nj->n",R,ic,R); diff=ours-theirs
print("diff mean %.5f sd %.5f min %.5f max %.5f"%(diff.mean(),diff.std(),diff.min(),diff.max()))
s=np.polyfit(theirs,diff,1); print("diff vs their chi2: slope %.5f intercept %.5f corr %.3f"%(s[0],s[1],np.corrcoef(theirs,diff)[0,1]))
k=0.99397; pred=(1/k-1)*theirs
print("cov*0.99397 model: predicted diff mean %.5f min %.5f; residual sd after model %.5f"%(pred.mean(),pred.min(),(diff-pred).std()))
# best uniform rescale by least squares
kk=np.sum(ours*theirs)/np.sum(ours*ours); print("LSQ rescale of chi2: theirs = %.5f * ours, resid sd %.5f"%(kk,(theirs-kk*ours).std()))
# rounded data vector (Table 1 two decimals)
for nd in (2,3,4):
    vr=np.round(val,nd); Rr=vr-T; c2=np.einsum("ni,ij,nj->n",Rr,ic,Rr); e=c2-theirs
    print("data rounded to %d dp: diff mean %+.5f sd %.5f"%(nd,e.mean(),e.std()))
# linear solve for data shift delta: diff = -2 g.R + c  (g = C^-1 delta)
A=np.hstack([-2*R,np.ones((len(R),1))]); sol,*_=np.linalg.lstsq(A,diff,rcond=None)
g=sol[:12]; delta=cov@g
print("fitted delta (data_ours - data_theirs), units of sigma_diag:"); 
for zz,k_,dl,sd in zip(z,kind,delta,np.sqrt(np.diag(cov))): print("  %.3f %s  %+.5f  (%+.3f sd)"%(zz,k_,dl,dl/sd))
# check: chi2 with shifted data
v2=val-delta; R2=v2-T; c2=np.einsum("ni,ij,nj->n",R2,ic,R2); print("after shift: diff mean %+.6f sd %.6f ; delta^T C^-1 delta %.5f fitted const %.5f"%((c2-theirs).mean(),(c2-theirs).std(),delta@ic@delta,sol[12]))
