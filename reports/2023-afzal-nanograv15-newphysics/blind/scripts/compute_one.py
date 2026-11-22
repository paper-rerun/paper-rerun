"""Compute the Table 4 estimators for one model/analysis, per PREREG.md section 3.

usage: compute_one.py <model> <NP|NPSMBHB> <chains_dir> <out_json>
"""
import ctypes, json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
from safeload import load_chain

# Low priority: the GPU and the rest of the machine belong to the user.
try:
    ctypes.windll.kernel32.SetPriorityClass(ctypes.windll.kernel32.GetCurrentProcess(), 0x00000040)
except Exception as e:
    print('priority: %r' % (e,), file=sys.stderr)

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PRIORS = json.load(open(os.path.join(HERE, 'out', 'priors.json')))

# model -> deposit file stem. The paper's dw-dr is the deposit's dw_ds.
FILESTEM = {
    'igw': 'igw', 'sigw-delta': 'sigw_delta', 'sigw-gauss': 'sigw_gauss',
    'sigw-box': 'sigw_box', 'pt-bubble': 'pt_bubble', 'pt-sound': 'pt_sound',
    'stable-c': 'stable_c', 'stable-k': 'stable_k', 'stable-m': 'stable_m',
    'stable-n': 'stable_n', 'meta-l': 'meta_l', 'meta-ls': 'meta_ls',
    'super': 'super', 'dw-sm': 'dw_sm', 'dw-dr': 'dw_ds',
}

# paper symbol -> chain column name, per model where it differs
COLNAME = {
    'log10_A_bhb': 'gw_bhb_np_0',
    'gamma_bhb': 'gw_bhb_np_1',
    'log10_alpha_star': 'log10_alpha',
    'log10_HR': 'log10_H_R',
    'log10_f_min': 'log10_fmin',
    'log10_f_max': 'log10_fmax',
    'Delta': 'width',
    'log10_dNeff': 'log10_N_eff',
}
COLNAME_BY_MODEL = {
    ('sigw-delta', 'log10_f_star'): 'log10_f_peak',
    ('sigw-gauss', 'log10_f_star'): 'log10_fpeak',
}

BHB_SD = {'log10_A_bhb': 0.5291502622129181, 'gamma_bhb': 0.3464101615137755}
BHB_MEAN = {'log10_A_bhb': -15.6, 'gamma_bhb': 4.7}


def shortest_interval(x_sorted, frac=0.68):
    n = x_sorted.size
    k = int(round(frac * n))
    if k >= n:
        return float(x_sorted[0]), float(x_sorted[-1])
    widths = x_sorted[k:] - x_sorted[:n - k]
    i = int(np.argmin(widths))
    return float(x_sorted[i]), float(x_sorted[i + k])


def smoothed_density(x, lo, hi, h, nbins=4000):
    """Histogram + Gaussian convolution = KDE evaluated on a grid (no scipy here)."""
    counts, edges = np.histogram(x, bins=nbins, range=(lo, hi))
    centres = 0.5 * (edges[1:] + edges[:-1])
    bw = (hi - lo) / nbins
    sig = h / bw
    if sig < 0.5:
        sig = 0.5
    half = int(np.ceil(4 * sig))
    t = np.arange(-half, half + 1, dtype=float)
    kern = np.exp(-0.5 * (t / sig) ** 2)
    kern /= kern.sum()
    dens = np.convolve(counts.astype(float), kern, mode='same')
    return centres, dens


def levelset_interval(centres, dens, frac=0.68):
    total = dens.sum()
    order = np.argsort(dens)[::-1]
    csum = np.cumsum(dens[order])
    cut = np.searchsorted(csum, frac * total)
    keep = order[:cut + 1]
    return float(centres[keep].min()), float(centres[keep].max())


def main():
    model, analysis, chains_dir, out_json = sys.argv[1:5]
    stem = FILESTEM[model]
    fname = stem + ('_bhb' if analysis == 'NPSMBHB' else '') + '.pkl.gz'
    path = os.path.join(chains_dir, fname)

    params, arr = load_chain(path)
    keys = list(params.keys())
    idx = {k: i for i, k in enumerate(keys)}

    wanted = list(PRIORS[model].keys())
    if analysis == 'NPSMBHB':
        wanted = wanted + ['log10_A_bhb', 'gamma_bhb']

    res = {'model': model, 'analysis': analysis, 'file': fname,
           'nsamples': int(arr.shape[0]), 'ncols': int(arr.shape[1]),
           'nkeys': len(keys), 'params': {}}

    for p in wanted:
        col = COLNAME_BY_MODEL.get((model, p), COLNAME.get(p, p))
        if col not in idx:
            res['params'][p] = {'error': 'column %r not in chain' % col}
            continue
        x = np.array(arr[:, idx[col]], dtype=float)
        if p in BHB_SD:
            lo, hi = float(x.min()), float(x.max())
            prior_range = None
        else:
            lo, hi = PRIORS[model][p]
            prior_range = [lo, hi]
        xs = np.sort(x)
        mean = float(x.mean())
        sd0 = float(x.std(ddof=0))
        sd1 = float(x.std(ddof=1))
        hpd_lo, hpd_hi = shortest_interval(xs)

        h_scott = sd0 * x.size ** (-0.2)
        bands = {'scott': h_scott}
        for frac in (0.005, 0.01, 0.02, 0.05):
            bands['r%g' % frac] = frac * (hi - lo)

        dens_out = {}
        for tag, h in bands.items():
            cc, dd = smoothed_density(x, lo, hi, h)
            dens_out[tag] = {
                'h': float(h),
                'maxpost': float(cc[int(np.argmax(dd))]),
                'hpd68_levelset': list(levelset_interval(cc, dd)),
                'hpd95_levelset': list(levelset_interval(cc, dd, 0.95)),
            }

        res['params'][p] = {
            'column': col, 'n': int(x.size), 'prior_range': prior_range,
            'sample_min': float(x.min()), 'sample_max': float(x.max()),
            'mean': mean, 'sd_ddof0': sd0, 'sd_ddof1': sd1,
            'hpd68_shortest': [hpd_lo, hpd_hi],
            'pct_16_84': [float(np.percentile(x, 16)), float(np.percentile(x, 84))],
            'density': dens_out,
        }
        # secondary diagnostic: drop the first 25% of the chain
        cut = x.size // 4
        xb = x[cut:]
        xbs = np.sort(xb)
        bl, bh = shortest_interval(xbs)
        res['params'][p]['burn25'] = {
            'mean': float(xb.mean()), 'sd': float(xb.std(ddof=0)),
            'hpd68_shortest': [bl, bh]}

    del arr
    json.dump(res, open(out_json, 'w'), indent=1)
    print('ok %s %s n=%d -> %s' % (model, analysis, res['nsamples'], out_json))


if __name__ == '__main__':
    main()
