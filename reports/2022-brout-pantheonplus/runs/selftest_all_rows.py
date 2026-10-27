"""Distance self-test on every data row: our Gauss-Legendre distances against adaptive quad, same 6 cosmologies as pp_like._selftest"""
import numpy as np
from scipy.integrate import quad
import pp_like

like = pp_like.PantheonPlus()
zs = like.zHD[like.hub]
zhel = like.zHEL[like.hub]
worst = 0.0
for om, ok, w0, wa in [(0.334, 0.0, -1.0, 0.0), (0.3, -0.2, -1.0, 0.0), (0.3, 0.3, -1.0, 0.0),
                       (0.31, 0.0, -0.9, 0.0), (0.4, 0.0, -0.93, -1.5), (0.2, 0.0, -0.8, 1.0)]:
    mu = like.mu_cosmo(om, 0.7, ok, w0, wa)
    # Cumulative quad between sorted redshifts, so every row is checked at low cost
    order = np.argsort(zs)
    dc_sorted = np.zeros(len(zs))
    z_prev, acc = 0.0, 0.0
    for k, i in enumerate(order):
        acc += quad(lambda x: 1.0 / np.sqrt(like.e2(x, om, ok, w0, wa)), z_prev, zs[i], epsabs=0, epsrel=1e-12)[0]
        dc_sorted[k] = acc
        z_prev = zs[i]
    dc = np.empty(len(zs))
    dc[order] = dc_sorted
    if ok > 0:
        dm = np.sinh(np.sqrt(ok) * dc) / np.sqrt(ok)
    elif ok < 0:
        dm = np.sin(np.sqrt(-ok) * dc) / np.sqrt(-ok)
    else:
        dm = dc
    ref = 5 * np.log10((1 + zs) * (1 + zhel) * pp_like.C_KMS / 70.0 * dm / (1 + zs)) + 25
    dmu = np.abs(mu - ref)
    # 1e-6 relative in distance is 2.2e-6 mag
    rel = np.max(dmu) / (5 / np.log(10))
    worst = max(worst, rel)
    print("Om=%.3f Ok=%.2f w0=%.2f wa=%.2f rows=%d max|dmu|=%.3e mag max rel dist err=%.3e" % (om, ok, w0, wa, len(mu), dmu.max(), rel))
print("all rows, all cosmologies: max relative distance error %.3e, below 1e-6: %s" % (worst, worst < 1e-6))
