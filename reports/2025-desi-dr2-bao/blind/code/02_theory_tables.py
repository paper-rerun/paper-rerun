# Precompute the two CAMB tables the grids need:
#   1) A(Omega_m) = h*distance at each data redshift (h-independent to ~1e-4)
#   2) r_drag(omega_b, omega_m) on a table, since r_d depends only on these two here
import json, os, sys, time
import numpy as np
from multiprocessing import Pool
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import load_data, model_A, camb_background, ROOT, H_REF

OM_GRID = np.linspace(0.230, 0.370, 281)
WB_TAB = np.linspace(0.0180, 0.0264, 29)
WM_TAB = np.linspace(0.0900, 0.2100, 41)

z, d, kinds, cov = load_data()


def job_A(om):
    A, rd = model_A(z, kinds, om, h=H_REF)
    return A


def job_rd(args):
    wb, wm = args
    # pick any h, r_d only cares about omega_b and omega_m; use h so that Omega_m stays sane
    h = 0.70
    om = wm / (h * h)
    try:
        _, _, rd = camb_background(om, h=h, omega_b=wb)
    except ValueError:
        return np.nan
    return rd


if __name__ == "__main__":
    t0 = time.time()
    with Pool(4) as p:
        A_list = p.map(job_A, OM_GRID, chunksize=4)
    A_tab = np.array(A_list)
    print("A table done in %.1f s, shape %s" % (time.time() - t0, A_tab.shape))

    pairs = [(wb, wm) for wb in WB_TAB for wm in WM_TAB]
    t0 = time.time()
    with Pool(4) as p:
        rd_list = p.map(job_rd, pairs, chunksize=8)
    rd_tab = np.array(rd_list).reshape(len(WB_TAB), len(WM_TAB))
    print("rd table done in %.1f s, nan count %d" % (time.time() - t0, int(np.isnan(rd_tab).sum())))

    # --- check: residual h-dependence of A at fixed Omega_m
    hcheck = {}
    for om in (0.26, 0.2975, 0.34):
        a0 = model_A(z, kinds, om, h=0.64)[0]
        a1 = model_A(z, kinds, om, h=H_REF)[0]
        a2 = model_A(z, kinds, om, h=0.72)[0]
        hcheck[str(om)] = float(np.max(np.abs(np.array([a0, a2]) - a1) / a1))
    print("max fractional h-dependence of A over h in [0.64,0.72]:", hcheck)

    np.savez(os.path.join(ROOT, "out", "theory_tables.npz"),
             om_grid=OM_GRID, A_tab=A_tab, wb_tab=WB_TAB, wm_tab=WM_TAB, rd_tab=rd_tab)
    with open(os.path.join(ROOT, "out", "theory_tables_checks.json"), "w") as f:
        json.dump({"A_h_dependence_max_fractional": hcheck,
                   "rd_tab_min": float(rd_tab.min()), "rd_tab_max": float(rd_tab.max()),
                   "n_camb_distance_calls": len(OM_GRID),
                   "n_camb_rd_calls": len(pairs)}, f, indent=2)
    print("saved")
