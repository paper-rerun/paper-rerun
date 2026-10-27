"""Pantheon+ likelihoods in plain numpy, following the authors' CosmoSIS modules
(Pantheon+_only_cosmosis_likelihood.py and Pantheon+SH0ES_cosmosis_likelihood.py @ f959603b55).
Background is analytic (D-BACKGROUND main); CAMB is only used as a check in camb_check.py.
"""
import os
import numpy as np
import pandas as pd

ROOT = "/mnt/e/Ciencia/noturno/2022-brout-pantheonplus"
DATA_FILE = os.path.join(ROOT, "data", "Pantheon+SH0ES.dat")
COV_FILE = os.path.join(ROOT, "data", "Pantheon+SH0ES_STAT+SYS.cov")
C_KMS = 299792.458

# Gauss-Legendre nodes for each segment between consecutive data redshifts
GL_X, GL_W = np.polynomial.legendre.leggauss(8)


def read_full_covariance(path=COV_FILE):
    # First line is N, then N*N values one per line, row-major (as the authors' nested loops read them)
    values = np.loadtxt(path)
    n = int(values[0])
    assert values.size == 1 + n * n, values.size
    return values[1:].reshape(n, n)


class PantheonPlus:
    def __init__(self, use_sh0es=False, cov=None):
        data = pd.read_csv(DATA_FILE, delim_whitespace=True)
        self.origlen = len(data)
        if use_sh0es:
            ww = (data["zHD"] > 0.01) | (np.array(data["IS_CALIBRATOR"], dtype=bool))
        else:
            ww = data["zHD"] > 0.01
        self.mask = np.array(ww, dtype=bool)
        self.zHD = np.array(data["zHD"][self.mask], dtype=float)
        self.zHEL = np.array(data["zHEL"][self.mask], dtype=float)
        self.m_obs = np.array(data["m_b_corr"][self.mask], dtype=float)
        self.n = int(self.mask.sum())
        if use_sh0es:
            self.is_cal = np.array(data["IS_CALIBRATOR"][self.mask], dtype=bool)
            self.ceph = np.array(data["CEPH_DIST"][self.mask], dtype=float)
        else:
            self.is_cal = np.zeros(self.n, dtype=bool)
            self.ceph = np.zeros(self.n)
        full = read_full_covariance() if cov is None else cov
        assert full.shape == (self.origlen, self.origlen)
        self.cov = full[np.ix_(self.mask, self.mask)]
        # GaussianLikelihood inverts the covariance once
        self.icov = np.linalg.inv(self.cov)

        # Integration grid for the comoving distance: segments between sorted unique redshifts
        hub = ~self.is_cal
        zu = np.unique(self.zHD[hub])
        edges = np.concatenate([[0.0], zu])
        lo, hi = edges[:-1], edges[1:]
        half = 0.5 * (hi - lo)
        mid = 0.5 * (hi + lo)
        self.nodes = (mid[:, None] + half[:, None] * GL_X[None, :])  # (nseg, 8)
        self.node_w = half[:, None] * GL_W[None, :]
        self.z_unique = zu
        self.hub_index = np.searchsorted(zu, self.zHD[hub])
        self.hub = hub
        self.zmax = zu[-1]
        # E^2 > 0 is checked at the integration nodes and the segment edges
        self.edges = edges

    @staticmethod
    def e2(z, om, ok, w0, wa):
        ode = 1.0 - om - ok
        a1 = 1.0 + z
        if wa == 0.0:
            f = a1 ** (3.0 * (1.0 + w0))
        else:
            # CPL w(a) = w0 + wa (1 - a)
            f = a1 ** (3.0 * (1.0 + w0 + wa)) * np.exp(-3.0 * wa * z / a1)
        return om * a1 ** 3 + ok * a1 ** 2 + ode * f

    def mu_cosmo(self, om, h, ok=0.0, w0=-1.0, wa=0.0):
        """5 log10[(1+zHD)(1+zHEL) D_A(zHD)/Mpc] + 25 for the Hubble-flow rows, None if undefined"""
        e2_nodes = self.e2(self.nodes, om, ok, w0, wa)
        if np.any(e2_nodes <= 0.0) or np.any(self.e2(self.edges, om, ok, w0, wa) <= 0.0):
            return None
        inv_e = 1.0 / np.sqrt(e2_nodes)
        seg = np.sum(inv_e * self.node_w, axis=1)
        dc_unit = np.cumsum(seg)  # comoving distance in units of c/H0
        if ok > 0.0:
            sk = np.sqrt(ok)
            dm_unit = np.sinh(sk * dc_unit) / sk
        elif ok < 0.0:
            sk = np.sqrt(-ok)
            dm_unit = np.sin(sk * dc_unit) / sk
        else:
            dm_unit = dc_unit
        if np.any(dm_unit <= 0.0):
            return None
        dh = C_KMS / (100.0 * h)
        z = self.zHD[self.hub]
        zh = self.zHEL[self.hub]
        d_a = dh * dm_unit[self.hub_index] / (1.0 + z)
        return 5.0 * np.log10((1.0 + z) * (1.0 + zh) * d_a) + 25.0

    def theory(self, M, om, h, ok=0.0, w0=-1.0, wa=0.0):
        mu = self.mu_cosmo(om, h, ok, w0, wa)
        if mu is None:
            return None
        out = np.empty(self.n)
        out[self.hub] = mu
        out[self.is_cal] = self.ceph[self.is_cal]
        return out + M

    def chi2(self, M, om, h, ok=0.0, w0=-1.0, wa=0.0):
        t = self.theory(M, om, h, ok, w0, wa)
        if t is None:
            return np.inf
        r = self.m_obs - t
        return float(r @ (self.icov @ r))

    def chi2_margM(self, om, ok=0.0, w0=-1.0, wa=0.0):
        """Cobaya-style analytic marginalisation over M (h fixed at 0.7; it is absorbed by M)"""
        t = self.theory(0.0, om, 0.7, ok, w0, wa)
        if t is None:
            return np.inf
        r = self.m_obs - t
        a = self.icov @ r
        ones_w = self.icov.sum(axis=0)
        e = ones_w.sum()
        b = ones_w @ r
        return float(r @ a - b * b / e)


def _selftest():
    from scipy.integrate import quad
    like = PantheonPlus()
    assert like.n == 1590, like.n
    # Distances against adaptive quad for a few cosmologies (relative error < 1e-6)
    for om, ok, w0, wa in [(0.334, 0.0, -1.0, 0.0), (0.3, -0.2, -1.0, 0.0), (0.3, 0.3, -1.0, 0.0),
                           (0.31, 0.0, -0.9, 0.0), (0.4, 0.0, -0.93, -1.5), (0.2, 0.0, -0.8, 1.0)]:
        mu = like.mu_cosmo(om, 0.7, ok, w0, wa)
        for i in [0, 500, 1000, len(mu) - 1]:
            z = like.zHD[like.hub][i]
            dc = quad(lambda x: 1.0 / np.sqrt(like.e2(x, om, ok, w0, wa)), 0.0, z, epsabs=0, epsrel=1e-12)[0]
            if ok > 0:
                dm = np.sinh(np.sqrt(ok) * dc) / np.sqrt(ok)
            elif ok < 0:
                dm = np.sin(np.sqrt(-ok) * dc) / np.sqrt(-ok)
            else:
                dm = dc
            ref = 5 * np.log10((1 + z) * (1 + like.zHEL[like.hub][i]) * C_KMS / 70.0 * dm / (1 + z)) + 25
            # 1e-6 relative in distance is 2.2e-6 mag
            assert abs(mu[i] - ref) < 2.2e-6, (om, ok, w0, wa, i, mu[i] - ref)
    print("selftest ok, n =", like.n)


if __name__ == "__main__":
    _selftest()
