"""Check our covariance read against the authors' loop, run the distance self-test and time one likelihood call"""
import time
import numpy as np
import pandas as pd
import pp_like

pp_like._selftest()
data = pd.read_csv(pp_like.DATA_FILE, delim_whitespace=True)
print("rows", len(data), "zHD>0.01:", int((data["zHD"] > 0.01).sum()),
      "calibrators:", int(data["IS_CALIBRATOR"].sum()),
      "calibrators with zHD>0.01:", int(((data["zHD"] > 0.01) & (data["IS_CALIBRATOR"] == 1)).sum()),
      "sh0es rows:", int(((data["zHD"] > 0.01) | (data["IS_CALIBRATOR"] == 1)).sum()),
      "max zHD:", data["zHD"].max())

# Authors' loop from Pantheon+_only_cosmosis_likelihood.py build_covariance, verbatim logic
ww = data["zHD"] > 0.01
origlen = len(data)
n = int(ww.sum())
C = np.zeros((n, n))
wwa = np.array(ww)
with open(pp_like.COV_FILE) as f:
    f.readline()
    ii = -1
    for i in range(origlen):
        jj = -1
        if wwa[i]:
            ii += 1
        for j in range(origlen):
            if wwa[j]:
                jj += 1
            val = float(f.readline())
            if wwa[i]:
                if wwa[j]:
                    C[ii, jj] = val
like = pp_like.PantheonPlus()
print("authors loop == ours:", np.array_equal(C, like.cov), "symmetric:", np.allclose(like.cov, like.cov.T),
      "min eig:", np.linalg.eigvalsh(like.cov).min(), "C[0,0]_full:", pp_like.read_full_covariance()[0, 0])

t = time.time()
for k in range(500):
    like.chi2(-19.25, 0.334 + 1e-5 * k, 0.7)
print("ms per chi2: %.3f" % ((time.time() - t) / 500 * 1e3))
print("chi2 at Om=0.334 h=0.7 M=-19.25:", like.chi2(-19.25, 0.334, 0.7))
