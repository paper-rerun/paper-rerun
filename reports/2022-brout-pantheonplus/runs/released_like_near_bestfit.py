"""Same 1000 points per released chain as released_like_check.py (rng seed 0), split into points within 10 of the best ln L and the tail"""
import gzip
import json
import os
import numpy as np
import pp_like

# Same chains and reader as released_like_check.py (copied, since importing it would rerun it)
CH = os.path.join(pp_like.ROOT, "sources", "repo", "5_COSMOLOGY", "chains")
FILES = {
    "flcdm": ("Pantheon+Only/Pantheon+only_FlatLambdaCDM.txt.gz", False),
    "lcdm": ("Pantheon+Only/Pantheon+only_LambdaCDM.txt.gz", False),
    "fwcdm": ("Pantheon+Only/Pantheon+only_FlatwCDM.txt.gz", False),
    "fw0wa": ("Pantheon+Only/Pantheon+only_Flatw0waCDM.txt.gz", False),
    "sh0esflcdm": ("Pantheon+SH0ES/Pantheon+SH0ES_FlatLambdaCDM.txt.gz", True),
}


def read_chain(path):
    with gzip.open(path, "rt") as f:
        header = f.readline().lstrip("#").split()
        rows = np.loadtxt(f, comments="#")
    return [h.split("--")[-1] for h in header], rows

out = {}
likes = {}
rng = np.random.default_rng(0)
for key, (rel, sh0es) in FILES.items():
    names, rows = read_chain(os.path.join(CH, rel))
    if sh0es not in likes:
        likes[sh0es] = pp_like.PantheonPlus(use_sh0es=sh0es)
    like = likes[sh0es]
    idx = rng.choice(len(rows), size=min(1000, len(rows)), replace=False)
    col = {n: i for i, n in enumerate(names)}
    theirs, ours, pts = [], [], []
    for i in idx:
        r = rows[i]
        om = r[col["omega_m"]]
        ok = r[col["omega_k"]] if "omega_k" in col else 0.0
        w0 = r[col["w"]] if "w" in col else -1.0
        wa = r[col["wa"]] if "wa" in col else 0.0
        theirs.append(r[col["post"]] - r[col["prior"]])
        ours.append(-0.5 * like.chi2(r[col["m"]], om, r[col["h0"]], ok, w0, wa))
        pts.append(dict(omega_m=om, h0=r[col["h0"]], omega_k=ok, w0=w0, wa=wa, m=r[col["m"]]))
    theirs, ours = np.array(theirs), np.array(ours)
    fin = np.isfinite(ours) & np.isfinite(theirs)
    d = ours[fin] - theirs[fin]
    near = theirs[fin] > theirs[fin].max() - 10.0
    dn = d[near]
    nonfinite = [dict(pts[k], ours=float(ours[k]), theirs=float(theirs[k])) for k in np.where(~fin)[0]]
    out[key] = dict(n_points=int(len(idx)), n_finite=int(fin.sum()), nonfinite_points=nonfinite,
                    n_near=int(near.sum()), near_diff_median=float(np.median(dn)), near_diff_std=float(np.std(dn)),
                    near_diff_max_abs_minus_median=float(np.max(np.abs(dn - np.median(dn)))),
                    all_diff_std=float(np.std(d)))
    print(key, json.dumps(out[key]))
json.dump(out, open(os.path.join(pp_like.ROOT, "runs", "out", "released_like_near_bestfit.json"), "w"), indent=1)
