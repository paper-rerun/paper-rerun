"""DIAGNOSTIC: our chi2 at the best point of DESI's BAO-only chain, and our exact minimum"""
import os
import sys

import numpy as np
from scipy.optimize import minimize

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import desi_bao  # noqa: E402

Path = os.path.join(desi_bao.ROOT, "data/desi_chains/cobaya/base/desi-bao-all/chain.1.txt")
Header = open(Path).readline().lstrip("#").split()
Data = np.loadtxt(Path)
Best = Data[np.argmin(Data[:, Header.index("chi2__BAO")])]
Hrd = Best[Header.index("hrdrag")]
Omm = Best[Header.index("omm")]
TheirChi2 = Best[Header.index("chi2__BAO")]


def OurChi2(OmegaM, RdH, H0, Ombh2):
	Model, _ = desi_bao.DistancesTimesH0(H0, OmegaM, Ombh2, False)
	return desi_bao.Chi2(Model * (H0 / 100.0) / RdH)


print(f"DESI best: omm {Omm:.6f} hrdrag {Hrd:.5f} their chi2 {TheirChi2:.6f}")
print(f"our chi2 at that point (H0=67.36, ombh2=0.02237 as in their yaml): {OurChi2(Omm, Hrd, 67.36, 0.02237):.6f}")
Res = minimize(lambda P: OurChi2(P[0], P[1], 68.0, 0.02218), [0.294, 101.9], method="Nelder-Mead", options={"xatol": 1e-7, "fatol": 1e-9})
print("our exact minimum (h=0.68):", Res.x, Res.fun)
