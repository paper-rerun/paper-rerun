# Shared pieces for the blind DESI DR2 BAO rerun: data loading and CAMB background
import os
import numpy as np

C_KMS = 299792.458
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(ROOT, "data", "bao_data", "desi_bao_dr2")
MEAN_FILE = os.path.join(DATA_DIR, "desi_gaussian_bao_ALL_GCcomb_mean.txt")
COV_FILE = os.path.join(DATA_DIR, "desi_gaussian_bao_ALL_GCcomb_cov.txt")

# Fixed physics, frozen in claims.json
MNU = 0.06
NNU = 3.044
TCMB = 2.7255
H_REF = 0.68


def load_data():
    z, val, kind = [], [], []
    with open(MEAN_FILE) as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            a, b, c = line.split()
            z.append(float(a))
            val.append(float(b))
            kind.append(c)
    cov = np.loadtxt(COV_FILE)
    return np.array(z), np.array(val), kind, cov


def camb_background(omega_m, h=H_REF, omega_b=0.02218):
    """Return h*DM, h*DH, h*DV in Mpc at the data redshifts, plus rdrag in Mpc."""
    import camb
    pars = camb.CAMBparams()
    pars.set_cosmology(H0=100.0 * h, ombh2=omega_b, omch2=0.12,
                       mnu=MNU, num_massive_neutrinos=1, nnu=NNU, omk=0.0, TCMB=TCMB)
    omnuh2 = pars.omnuh2
    omch2 = omega_m * h * h - omega_b - omnuh2
    if omch2 <= 0:
        raise ValueError("omch2 <= 0 for omega_m=%r h=%r" % (omega_m, h))
    pars.set_cosmology(H0=100.0 * h, ombh2=omega_b, omch2=omch2,
                       mnu=MNU, num_massive_neutrinos=1, nnu=NNU, omk=0.0, TCMB=TCMB)
    res = camb.get_background(pars)
    rd = res.get_derived_params()["rdrag"]
    return res, omnuh2, rd


def model_A(zs, kinds, omega_m, h=H_REF, omega_b=0.02218):
    """A_i = (h * distance) in Mpc, so that model_i = A_i / (h*rd). h-independent to ~1e-4."""
    res, _, rd = camb_background(omega_m, h, omega_b)
    out = np.zeros(len(zs))
    for i, (zi, ki) in enumerate(zip(zs, kinds)):
        DM = res.angular_diameter_distance(zi) * (1.0 + zi)
        DH = C_KMS / res.hubble_parameter(zi)
        if ki == "DM_over_rs":
            d = DM
        elif ki == "DH_over_rs":
            d = DH
        elif ki == "DV_over_rs":
            d = (zi * DM * DM * DH) ** (1.0 / 3.0)
        else:
            raise ValueError("unknown quantity " + ki)
        out[i] = d * h
    return out, rd
