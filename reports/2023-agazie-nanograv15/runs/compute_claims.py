# Compute the pre-registered claims (claims.json) from the authors' published cores
import sys, json, hashlib
import numpy as np
W = sys.argv[1]
REPO = W + '/sources/repo'
sys.path.insert(0, REPO + '/tutorials')  # authors' extra_functions.py, unmodified
import extra_functions
from la_forge import core, slices
from emcee.autocorr import integrated_time

P = REPO + '/tutorials/presampled_cores/'
out = {}
print('claims.json sha256', hashlib.sha256(open(W + '/claims.json', 'rb').read()).hexdigest())

def q(x):
    p05, p50, p95 = np.percentile(x, [5, 50, 95])
    return dict(p05=p05, median=p50, p95=p95, plus=p95 - p50, minus=p50 - p05, n=int(x.size))

def inband(v, band):
    return bool(band[0] <= v <= band[1])

# ---- C1: hd13/3 amplitude from the HD branch of the product-space core
c = core.Core(corepath=P + 'curn_hd.core')
nm = c.get_param('nmodel')
logA_hd = c.get_param('gw_hd_log10_A')
logA_crn = c.get_param('gw_crn_log10_A')
print('curn_hd: rows', c.chain.shape[0], 'burn', c.burn, 'post-burn', nm.size)
print('curn_hd params with gamma:', [p for p in c.params if 'gamma' in p and not p.startswith(('B', 'J'))])
hd_mask = nm > 0.5
A = 10 ** logA_hd[hd_mask]
r = q(A)
tau = integrated_time(logA_hd[hd_mask], quiet=True)[0]
r['tau_int_on_hd_branch_samples'] = float(tau)
r['neff_approx'] = float(A.size / tau)
band = {'median': [2.3e-15, 2.5e-15], 'p05': [1.7e-15, 1.9e-15], 'p95': [3.0e-15, 3.2e-15]}
r['inside'] = {k: inband(r[k], band[k]) for k in band}
out['C1_A_hd13_3'] = r
print('C1 A_hd (nmodel>0.5):', json.dumps(r, indent=1))
print('C1 HD-branch log10_A max', logA_hd[hd_mask].max(), ' fraction above -14:', np.mean(logA_hd[hd_mask] > -14))
# Sensitivity (not verdict): no burn-in
c0 = core.Core(corepath=P + 'curn_hd.core', burn=0)
nm0 = c0.get_param('nmodel'); la0 = c0.get_param('gw_hd_log10_A')
out['C1_sensitivity_burn0'] = q(10 ** la0[nm0 > 0.5])
print('C1 burn=0:', out['C1_sensitivity_burn0'])
# Supporting check on the fixed gamma: CURN branch vs the authors' CURN 13/3 ML amplitude
ml = json.load(open(REPO + '/tutorials/data/optstat_ml_gamma4p33.json'))['gw_log10_A']
cb = logA_crn[nm < 0.5]
out['gamma_check'] = dict(curn_branch_log10A=q(cb), curn13_3_ML_log10A_from_optstat_json=ml)
print('CURN branch log10_A', q(cb), ' authors CURN13/3 ML log10_A', ml)

# ---- S3: product-space BF, weight 300 from the authors' notebook
n_hd = int(np.sum(hd_mask)); n_crn = int(np.sum(nm < 0.5))
bf = n_hd / n_crn * 300
rng = np.random.default_rng(20231108)
bs = rng.choice(nm, (nm.size, 10_000))
ors = np.sum((bs > 0.5) & (bs <= 1.5), axis=0) / np.sum((bs > -0.5) & (bs <= 0.5), axis=0) * 300
tau_nm = integrated_time(nm, quiet=True)[0]
out['S3_BF_hd_vs_curn_productspace'] = dict(n_hd=n_hd, n_curn=n_crn, bf=bf, bs_mean=float(ors.mean()), bs_std=float(ors.std()),
    tau_int_nmodel=float(tau_nm), inside=inband(bf, [156, 296]))
print('S3', out['S3_BF_hd_vs_curn_productspace'])

# ---- TI: authors' ti_log_evidence, RNG replaced by a seeded one before each call
def lnZ(name, seed):
    extra_functions.rng = np.random.default_rng(seed)
    sc = slices.SlicesCore(corepath=P + name)
    return extra_functions.ti_log_evidence(sc)
lz_irn, s_irn = lnZ('irn_ti.core', 1)
lz_crn, s_crn = lnZ('curn_ti.core', 2)
lz_hd, s_hd = lnZ('hd_ti.core', 3)
ln10 = np.log(10)
def l10bf(a, sa, b, sb):
    return (b - a) / ln10, np.sqrt(sa ** 2 + sb ** 2) / ln10
v, s = l10bf(lz_irn, s_irn, lz_crn, s_crn)
out['S1_log10BF_curn_vs_irn'] = dict(lnZ_irn=lz_irn, sig_irn=s_irn, lnZ_curn=lz_crn, sig_curn=s_crn, log10_bf=v, sigma=s, inside=inband(v, [11.9, 12.3]))
v2, s2 = l10bf(lz_irn, s_irn, lz_hd, s_hd)
out['S2_log10BF_hd_vs_irn'] = dict(lnZ_hd=lz_hd, sig_hd=s_hd, log10_bf=v2, sigma=s2, inside=bool(v2 > 14), central_minus_2sigma_above_14=bool(v2 - 2 * s2 > 14))
v3, s3 = l10bf(lz_crn, s_crn, lz_hd, s_hd)
bf3 = 10 ** v3
out['S3b_BF_hd_vs_curn_ti'] = dict(log10_bf=v3, sigma_log10=s3, bf=bf3, bf_lo_1sig=10 ** (v3 - s3), bf_hi_1sig=10 ** (v3 + s3), inside=inband(bf3, [156, 296]))
for k in ('S1_log10BF_curn_vs_irn', 'S2_log10BF_hd_vs_irn', 'S3b_BF_hd_vs_curn_ti'):
    print(k, out[k])

# ---- E1: varied-gamma HD core vs paper's varied-gamma numbers
cv = core.Core(corepath=P + 'hd_14f_pl_vg.core')
g = cv.get_param('gw__gamma'); la = cv.get_param('gw__log10_A')
out['E1_vg_core_vs_paper'] = dict(A=q(10 ** la), gamma=q(g),
    inside={'A_median': inband(np.median(10 ** la), [6.3e-15, 6.5e-15]), 'gamma_median': inband(np.median(g), [3.15, 3.25])},
    tau_int_log10A=float(integrated_time(la, quiet=True)[0]))
print('E1', out['E1_vg_core_vs_paper'])

# ---- E3: conditional slice of the vg core at gamma ~ 13/3
m = np.abs(g - 13 / 3) < 0.1
out['E3_vg_conditional_slice'] = dict(n_slice=int(m.sum()), **(q(10 ** la[m]) if m.sum() > 2 else {}), gamma_max=float(g.max()))
print('E3', out['E3_vg_conditional_slice'])

# ---- E2: factorized-likelihood refit of the HD free spectrum at gamma = 13/3
cf = core.Core(corepath=P + 'hd_30f_fs.core')
T = 505861299.1401644; yr = 365.25 * 86400; gam = 13 / 3
f = np.arange(1, 15) / T
# Prior range adjusted to the core (samples reach -15.50, runs/fs_range.log); pre-registered fallback
edges = np.arange(-15.5, -4 + 1e-9, 0.05)
rhos = [cf.get_param(f'gw_hd_log10_rho_{i}') for i in range(14)]
print('free-spec log10_rho range in core (bins 1-14):', min(r_.min() for r_ in rhos), max(r_.max() for r_ in rhos))
grid = np.linspace(-18, -14, 4001)
logpost = np.zeros_like(grid)
for i in range(14):
    dens, _ = np.histogram(rhos[i], edges, density=True)
    lr = 0.5 * np.log10((10 ** grid) ** 2 / (12 * np.pi ** 2) * yr ** (3 - gam) * f[i] ** (-gam) / T)
    idx = np.clip(np.searchsorted(edges, lr) - 1, 0, dens.size - 1)
    d = np.where((lr < edges[0]) | (lr > edges[-1]), 0.0, dens[idx])
    logpost += np.log(d + 1e-250)
pst = np.exp(logpost - logpost.max()); cdf = np.cumsum(pst); cdf /= cdf[-1]
qq = {k: 10 ** np.interp(p, cdf, grid) for k, p in (('p05', 0.05), ('median', 0.5), ('p95', 0.95))}
out['E2_freespec_refit_A13_3'] = dict(**qq, nsamples_per_bin=int(rhos[0].size))
print('E2', out['E2_freespec_refit_A13_3'])

# ---- E4: Bayesian phase-shift p-value, as in make_fap_plots.ipynb
pb = np.load(REPO + '/data_release/figure_3/pshift_bfs.npy')
pv = len(np.where(pb > 226)[0]) / len(pb)
out['E4_bayesian_pvalue'] = dict(n=int(pb.size), n_above_226=int(np.sum(pb > 226)), p=pv, inside=inband(pv, [5e-4, 1.5e-3]),
    n_above_our_S3=int(np.sum(pb > bf)), p_at_our_S3=float(np.mean(pb > bf)))
print('E4', out['E4_bayesian_pvalue'])

json.dump(out, open(W + '/runs/results.json', 'w'), indent=1, default=float)
print('wrote runs/results.json')
