# Per-bin range of the free-spectrum core and the 13/3 power-law log10_rho at A = 2.4e-15
import sys, numpy as np
from la_forge import core
c = core.Core(corepath=sys.argv[1] + '/tutorials/presampled_cores/hd_30f_fs.core', burn=0)
T = 505861299.1401644; yr = 365.25 * 86400
for i in range(30):
    x = c.get_param(f'gw_hd_log10_rho_{i}')
    f = (i + 1) / T
    lr = 0.5 * np.log10((2.4e-15) ** 2 / (12 * np.pi ** 2) * yr ** (3 - 13 / 3) * f ** (-13 / 3) / T)
    print(i + 1, f'min {x.min():.4f} max {x.max():.4f} median {np.median(x):.3f} frac<-9 {np.mean(x < -9):.3f}  PL13/3(A=2.4e-15) {lr:.3f}')
