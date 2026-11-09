"""DESI 2024 VI, claims C1, C2, C3.

The posterior is evaluated on the dense grids fixed in claims.json and
marginalised exactly. No sampler, so no sampling scatter. CAMB supplies the
background expansion and the drag-epoch sound horizon.

Stages, each cached to runs/out so the script can be restarted:
  A  DM*h and c*h/H(z) on the (Omega_m, h) grid of the BAO+BBN fit, plus the
     single-h rows the BAO-alone fit needs.
  B  r_drag on an (omega_b, omega_m) grid, splined later.
  C  BAO alone: grid over (Omega_m, r_d h)  ->  C1, C2.
  D  BAO + BBN: grid over (Omega_m, H0, omega_b)  ->  C3.
"""
import json
import os
import sys
import time
from multiprocessing import Pool

import numpy as np
from scipy.interpolate import RectBivariateSpline

ROOT = "/mnt/e/Ciencia/noturno/2024-desi-bao-vi"
DATA = f"{ROOT}/data/bao_data"
OUT = f"{ROOT}/runs/out"
C_KMS = 299792.458

TCMB = 2.7255
NNU = 3.044
MNU = 0.06
OMNUH2 = 0.00064487          # CAMB's value for mnu=0.06, nnu=3.044 (probe.log)

# Grids, exactly as pre-registered in claims.json.
N_OM_C = 701
OM_C = np.linspace(0.15, 0.50, N_OM_C)          # BAO alone
RDH_C = np.linspace(90.0, 115.0, 701)
H_REF = 0.68
H_SENS = (0.64, 0.72)

OM_D = np.linspace(0.20, 0.42, 351)             # BAO + BBN
H0_D = np.linspace(63.0, 75.0, 351)
OB_D = np.linspace(0.0200, 0.0244, 61)
OB_BBN, OB_BBN_SIG = 0.02218, 0.00055

# r_d table. omega_m spans the whole (Omega_m, H0) box with room to spare.
OB_TAB = np.linspace(0.0195, 0.0249, 45)
OM2_TAB = np.linspace(0.070, 0.245, 120)


def load_data():
    z, val, kind = [], [], []
    with open(f"{DATA}/desi_2024_gaussian_bao_ALL_GCcomb_mean.txt") as fh:
        for line in fh:
            if line.startswith("#") or not line.strip():
                continue
            a, b, c = line.split()
            z.append(float(a)); val.append(float(b)); kind.append(c)
    cov = np.loadtxt(f"{DATA}/desi_2024_gaussian_bao_ALL_GCcomb_cov.txt")
    return np.array(z), np.array(val), kind, np.linalg.inv(cov)


Z, VAL, KIND, ICOV = load_data()
ZU = np.array(sorted(set(Z)))
# Index of each data point into the unique-redshift arrays.
ZIDX = np.array([int(np.where(ZU == zz)[0][0]) for zz in Z])
IS_DM = np.array([k == "DM_over_rs" for k in KIND])
IS_DH = np.array([k == "DH_over_rs" for k in KIND])
IS_DV = np.array([k == "DV_over_rs" for k in KIND])


# ---------------------------------------------------------------- stage A ----
def _dist_one(args):
    """Return DM(z)*h and c*h/H(z), both in Mpc, so that dividing by r_d h
    gives the observables directly. Imported lazily: CAMB in a worker."""
    import camb
    om, h = args
    omch2 = om * h * h - 0.02218 - OMNUH2
    if omch2 <= 0:
        return np.full(len(ZU), np.nan), np.full(len(ZU), np.nan)
    pars = camb.set_params(H0=100 * h, ombh2=0.02218, omch2=omch2,
                           mnu=MNU, nnu=NNU, omk=0.0, TCMB=TCMB)
    res = camb.get_background(pars)
    dm_h = res.comoving_radial_distance(ZU) * h
    dh_h = C_KMS * h / res.hubble_parameter(ZU)
    return dm_h, dh_h


def stage_a(tag, oms, hs, nproc):
    path = f"{OUT}/dist_{tag}.npz"
    if os.path.exists(path):
        print(f"[A:{tag}] cached")
        return np.load(path)
    jobs = [(om, h) for h in hs for om in oms]
    t0 = time.perf_counter()
    with Pool(nproc) as pool:
        got = pool.map(_dist_one, jobs, chunksize=64)
    dm = np.array([g[0] for g in got]).reshape(len(hs), len(oms), len(ZU))
    dh = np.array([g[1] for g in got]).reshape(len(hs), len(oms), len(ZU))
    print(f"[A:{tag}] {len(jobs)} CAMB calls in "
          f"{time.perf_counter() - t0:.1f} s, nan={int(np.isnan(dm).sum())}")
    np.savez_compressed(path, dm_h=dm, dh_h=dh, oms=oms, hs=hs, zu=ZU)
    return np.load(path)


# ---------------------------------------------------------------- stage B ----
def _rd_one(args):
    import camb
    ob, om2 = args
    omch2 = om2 - ob - OMNUH2
    if omch2 <= 0:
        return np.nan
    pars = camb.set_params(H0=68.0, ombh2=ob, omch2=omch2,
                           mnu=MNU, nnu=NNU, omk=0.0, TCMB=TCMB)
    # r_drag is set by the pre-recombination physics, so it depends on the
    # physical densities only. H0 here just fixes the Mpc unit, and r_drag
    # comes back in Mpc, so the choice of H0 does not enter.
    return camb.get_background(pars).get_derived_params()["rdrag"]


def stage_b(nproc):
    path = f"{OUT}/rd_table.npz"
    if os.path.exists(path):
        print("[B] cached")
        return np.load(path)
    jobs = [(ob, om2) for ob in OB_TAB for om2 in OM2_TAB]
    t0 = time.perf_counter()
    with Pool(nproc) as pool:
        got = pool.map(_rd_one, jobs, chunksize=32)
    rd = np.array(got).reshape(len(OB_TAB), len(OM2_TAB))
    print(f"[B] {len(jobs)} CAMB calls in {time.perf_counter() - t0:.1f} s, "
          f"nan={int(np.isnan(rd).sum())}, "
          f"r_d range {np.nanmin(rd):.2f}..{np.nanmax(rd):.2f} Mpc")
    np.savez_compressed(path, rd=rd, ob=OB_TAB, om2=OM2_TAB)
    return np.load(path)


def check_rd_spline(spline, nproc):
    """The spline has to reproduce direct CAMB at points it never saw."""
    rng = np.random.default_rng(20241108)
    pts = [(float(rng.uniform(0.0201, 0.0243)), float(rng.uniform(0.075, 0.240)))
           for _ in range(40)]
    with Pool(nproc) as pool:
        direct = np.array(pool.map(_rd_one, pts))
    interp = np.array([spline(ob, om2)[0, 0] for ob, om2 in pts])
    rel = np.abs(interp / direct - 1)
    print(f"[B] spline vs direct CAMB on 40 unseen points: worst relative "
          f"error {rel.max():.3e}, median {np.median(rel):.3e}")
    return float(rel.max())


# ------------------------------------------------------------ likelihood ----
def chi2_grid(dm_h, dh_h, rdh):
    """dm_h, dh_h: (..., nz). rdh: broadcastable to (...,). Returns chi2."""
    dm = dm_h[..., :] / rdh[..., None]
    dh = dh_h[..., :] / rdh[..., None]
    dv = (ZU * dm ** 2 * dh) ** (1.0 / 3.0)
    theory = np.empty(dm.shape[:-1] + (len(Z),))
    theory[..., IS_DM] = dm[..., ZIDX[IS_DM]]
    theory[..., IS_DH] = dh[..., ZIDX[IS_DH]]
    theory[..., IS_DV] = dv[..., ZIDX[IS_DV]]
    d = VAL - theory
    return np.einsum("...i,ij,...j->...", d, ICOV, d)


def marg(logp, axis_vals, axes_order):
    """Normalised 1D marginals of a log-posterior on a regular grid.
    Returns {name: (mean, sigma, edge_mass)}."""
    p = np.exp(logp - logp.max())
    out = {}
    for i, name in enumerate(axes_order):
        others = tuple(j for j in range(p.ndim) if j != i)
        m = p.sum(axis=others)
        m = m / m.sum()
        x = axis_vals[name]
        mean = float((m * x).sum())
        sig = float(np.sqrt((m * (x - mean) ** 2).sum()))
        edge = float(m[0] + m[-1])
        out[name] = (mean, sig, edge)
    return out


# ------------------------------------------------------------- stage C/D ----
def stage_c(nproc, results):
    d = stage_a("c", OM_C, np.array([H_REF, *H_SENS]), nproc)
    dm_all, dh_all, hs = d["dm_h"], d["dh_h"], d["hs"]
    for ih, h in enumerate(hs):
        dm = dm_all[ih][:, None, :]                  # (nom, 1, nz)
        dh = dh_all[ih][:, None, :]
        rdh = RDH_C[None, :]
        c2 = chi2_grid(np.broadcast_to(dm, (len(OM_C), len(RDH_C), len(ZU))),
                       np.broadcast_to(dh, (len(OM_C), len(RDH_C), len(ZU))),
                       np.broadcast_to(rdh, (len(OM_C), len(RDH_C))))
        got = marg(-0.5 * c2, {"Omega_m": OM_C, "rd_h": RDH_C},
                   ["Omega_m", "rd_h"])
        label = "main" if abs(h - H_REF) < 1e-12 else f"h={h:.2f}"
        print(f"[C] {label:8s} chi2_min={c2.min():.4f}  "
              f"Omega_m={got['Omega_m'][0]:.5f}+/-{got['Omega_m'][1]:.5f} "
              f"(edge {got['Omega_m'][2]:.1e})  "
              f"rd_h={got['rd_h'][0]:.4f}+/-{got['rd_h'][1]:.4f} "
              f"(edge {got['rd_h'][2]:.1e})")
        if abs(h - H_REF) < 1e-12:
            results["C1"] = {"mean": got["Omega_m"][0], "sigma": got["Omega_m"][1],
                             "edge_mass": got["Omega_m"][2]}
            results["C2"] = {"mean": got["rd_h"][0], "sigma": got["rd_h"][1],
                             "edge_mass": got["rd_h"][2]}
            results["C_chi2_min"] = float(c2.min())
        else:
            results.setdefault("C_sensitivity_h", {})[f"{h:.2f}"] = {
                "Omega_m": got["Omega_m"][:2], "rd_h": got["rd_h"][:2]}


def stage_d(nproc, results):
    hs = H0_D / 100.0
    d = stage_a("d", OM_D, hs, nproc)
    dm_all, dh_all = d["dm_h"], d["dh_h"]        # (nh0, nom, nz)
    tab = stage_b(nproc)
    spline = RectBivariateSpline(tab["ob"], tab["om2"], tab["rd"], kx=3, ky=3)
    results["rd_spline_worst_rel_err"] = check_rd_spline(spline, nproc)

    # r_d h on the (Omega_m, H0, omega_b) grid.
    om2 = OM_D[None, :, None] * (hs ** 2)[:, None, None]     # (nh0, nom, 1)
    om2 = np.broadcast_to(om2, (len(H0_D), len(OM_D), len(OB_D)))
    obg = np.broadcast_to(OB_D[None, None, :], om2.shape)
    rd = spline.ev(obg, om2)
    rdh = rd * hs[:, None, None]

    dm = np.broadcast_to(dm_all[:, :, None, :],
                         (len(H0_D), len(OM_D), len(OB_D), len(ZU)))
    dh = np.broadcast_to(dh_all[:, :, None, :], dm.shape)
    c2 = chi2_grid(dm, dh, rdh)
    c2 = c2 + ((OB_D - OB_BBN) / OB_BBN_SIG) ** 2        # Gaussian BBN prior
    got = marg(-0.5 * c2, {"H0": H0_D, "Omega_m": OM_D, "omega_b": OB_D},
               ["H0", "Omega_m", "omega_b"])
    print(f"[D] chi2_min={c2.min():.4f}")
    for k, (m, s, e) in got.items():
        print(f"[D] {k:9s} {m:.6f} +/- {s:.6f}  (edge mass {e:.1e})")
    results["C3"] = {"mean": got["H0"][0], "sigma": got["H0"][1],
                     "edge_mass": got["H0"][2]}
    results["D_extra"] = {k: {"mean": v[0], "sigma": v[1], "edge_mass": v[2]}
                          for k, v in got.items()}
    results["D_chi2_min"] = float(c2.min())


def main():
    nproc = int(os.environ.get("NPROC", "6"))
    print(f"nproc={nproc}")
    results = {}
    stage_c(nproc, results)
    stage_d(nproc, results)

    published = {"C1": (0.295, 0.015), "C2": (101.8, 1.3), "C3": (68.53, 0.80)}
    bands = {"C1": ((0.2920, 0.2980), (0.0135, 0.0165)),
             "C2": ((101.54, 102.06), (1.17, 1.43)),
             "C3": ((68.37, 68.69), (0.72, 0.88))}
    print("\n== verdict against the pre-registered bands ==")
    for cid in ("C1", "C2", "C3"):
        pv, ps = published[cid]
        ours = results[cid]
        (lo, hi), (slo, shi) = bands[cid]
        ok_m = lo <= ours["mean"] <= hi
        ok_s = slo <= ours["sigma"] <= shi
        results[cid].update({"published_mean": pv, "published_sigma": ps,
                             "band_mean": [lo, hi], "band_sigma": [slo, shi],
                             "mean_in_band": bool(ok_m),
                             "sigma_in_band": bool(ok_s),
                             "in_band": bool(ok_m and ok_s),
                             "shift_in_sigma": (ours["mean"] - pv) / ps})
        print(f"  {cid}: ours {ours['mean']:.4f} +/- {ours['sigma']:.4f} | "
              f"paper {pv} +/- {ps} | shift {(ours['mean']-pv)/ps:+.3f} sigma "
              f"| mean {'in' if ok_m else 'OUT'} | sigma {'in' if ok_s else 'OUT'}")
    with open(f"{OUT}/results.json", "w") as fh:
        json.dump(results, fh, indent=2, default=float)
    print(f"\nwritten {OUT}/results.json")


if __name__ == "__main__":
    sys.exit(main())
