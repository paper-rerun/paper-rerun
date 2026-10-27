"""One fit per call: python run_fit.py <run_name>. Writes out/<run_name>.npz and out/<run_name>.json; skips if the json exists.
Run names: <config>_<sampler>_s<seed>, e.g. flcdm_dynesty_s1, fw0wa4_emcee_s1.
"""
import json
import os
import sys
import time
import numpy as np
import pp_like

OUT = os.path.join(pp_like.ROOT, "runs", "out")

# Flat priors from the released chain headers (D-PARAMS-PRIORS); start = central value of values.ini
H0P = ("h0", 0.55, 0.91, 0.72)
MP = ("M", -20.0, -18.0, -19.0)
CONFIGS = {
    "flcdm": dict(like="only", params=[("Om", 0.1, 0.9, 0.33), H0P, MP]),
    "lcdm": dict(like="only", params=[("Om", 0.1, 0.9, 0.33), ("Ok", -1.0, 1.0, 0.0), H0P, MP]),
    "fwcdm": dict(like="only", params=[("Om", 0.1, 0.9, 0.33), ("w0", -2.0, 0.5, -1.0), H0P, MP]),
    "fw0wa4": dict(like="only", params=[("Om", 0.01, 0.9, 0.33), ("w0", -2.0, 0.5, -1.0), ("wa", -4.0, 4.0, 0.0),
                                        ("h0", 0.55, 0.91, 0.67), MP]),
    "fw0wa2": dict(like="only", params=[("Om", 0.01, 0.9, 0.33), ("w0", -2.0, 0.5, -1.0), ("wa", -2.0, 2.0, 0.0),
                                        ("h0", 0.55, 0.91, 0.67), MP]),
    "sh0esflcdm": dict(like="sh0es", params=[("Om", 0.1, 0.9, 0.33), H0P, MP]),
    # Variant D-NUISANCE-M-H0: M marginalised analytically (Cobaya sn.pantheonplus), h0 fixed
    "flcdmmargM": dict(like="margM", params=[("Om", 0.1, 0.9, 0.33)]),
}


def weighted_stats(x, w):
    w = w / w.sum()
    mean = float(np.sum(w * x))
    std = float(np.sqrt(np.sum(w * (x - mean) ** 2)))
    order = np.argsort(x)
    xs, ws = x[order], w[order]
    cdf = np.cumsum(ws) - 0.5 * ws
    p16, p50, p84 = (float(np.interp(q, cdf, xs)) for q in (0.16, 0.5, 0.84))
    # Shortest interval holding 68% of the weight (highest-density for a unimodal posterior)
    cw = np.cumsum(ws)
    best = (np.inf, xs[0], xs[-1])
    j = 0
    for i in range(len(xs)):
        start = cw[i] - ws[i]
        while j < len(xs) - 1 and cw[j] - start < 0.68:
            j += 1
        if cw[j] - start >= 0.68 and xs[j] - xs[i] < best[0]:
            best = (xs[j] - xs[i], xs[i], xs[j])
    return dict(mean=mean, std=std, p16=p16, p50=p50, p84=p84, plus=p84 - mean, minus=mean - p16,
                half_width=(p84 - p16) / 2, hpd68_lo=float(best[1]), hpd68_hi=float(best[2]))


def main(run):
    cfg_name, sampler_name, seed_tag = run.split("_")
    seed = int(seed_tag[1:])
    cfg = CONFIGS[cfg_name]
    os.makedirs(OUT, exist_ok=True)
    out_json = os.path.join(OUT, run + ".json")
    if os.path.exists(out_json):
        print("exists, skipping", run)
        return
    like = pp_like.PantheonPlus(use_sh0es=(cfg["like"] == "sh0es"))
    names = [p[0] for p in cfg["params"]]
    lo = np.array([p[1] for p in cfg["params"]])
    hi = np.array([p[2] for p in cfg["params"]])
    start = np.array([p[3] for p in cfg["params"]])
    ndim = len(names)

    def unpack(theta):
        d = dict(zip(names, theta))
        return d.get("M", 0.0), d["Om"], d.get("h0", 0.7), d.get("Ok", 0.0), d.get("w0", -1.0), d.get("wa", 0.0)

    ncall = [0]

    def loglike(theta):
        ncall[0] += 1
        M, om, h, ok, w0, wa = unpack(theta)
        if cfg["like"] == "margM":
            c2 = like.chi2_margM(om, ok, w0, wa)
        else:
            c2 = like.chi2(M, om, h, ok, w0, wa)
        return -0.5 * c2 if np.isfinite(c2) else -np.inf

    def logpost(theta):
        if np.any(theta < lo) or np.any(theta > hi):
            return -np.inf
        return loglike(theta)

    t0 = time.time()
    info = dict(run=run, config=cfg_name, sampler=sampler_name, seed=seed, n_data=like.n, params=names,
                prior_lo=lo.tolist(), prior_hi=hi.tolist())
    if sampler_name == "dynesty":
        import dynesty
        info["dynesty_version"] = dynesty.__version__

        def prior_transform(u):
            return lo + (hi - lo) * u

        # D-SAMPLER fallback: static nested sampling, 250 live points, rslice with 30 slices, dlogz 0.1
        # (logl_max guard: dynesty 1.2.3 cannot take -inf from the likelihood, so undefined cosmologies get -1e300)
        def loglike_ns(theta):
            v = loglike(theta)
            return v if np.isfinite(v) else -1e300

        sampler = dynesty.NestedSampler(loglike_ns, prior_transform, ndim, nlive=250, sample="rslice",
                                        slices=30, rstate=np.random.default_rng(seed))
        sampler.run_nested(dlogz=0.1, print_progress=True)
        res = sampler.results
        samples = res.samples
        logw = res.logwt - res.logz[-1]
        weights = np.exp(logw - logw.max())
        info.update(niter=int(res.niter), ncall_sampler=int(np.sum(res.ncall)), logz=float(res.logz[-1]),
                    logzerr=float(res.logzerr[-1]), n_samples=int(len(samples)),
                    ess_kish=float(weights.sum() ** 2 / np.sum(weights ** 2)))
        logl = res.logl
    elif sampler_name == "emcee":
        import emcee
        info["emcee_version"] = emcee.__version__
        nwalkers, nsteps = 16, 10000
        rs = np.random.RandomState(seed)
        # CosmoSIS emcee with random_start = F: a ball of 1e-3 of the prior width around the values.ini start
        p0 = start + 1e-3 * (hi - lo) * rs.randn(nwalkers, ndim)
        p0 = np.clip(p0, lo, hi)
        sampler = emcee.EnsembleSampler(nwalkers, ndim, logpost)
        sampler.random_state = rs.get_state()
        sampler.run_mcmc(p0, nsteps, progress=False)
        chain = sampler.get_chain()  # (nsteps, nwalkers, ndim)
        lp = sampler.get_log_prob()
        burn = int(0.3 * nsteps)
        np.savez_compressed(os.path.join(OUT, run + "_fullchain.npz"), chain=chain, log_prob=lp)
        samples = chain[burn:].reshape(-1, ndim)
        logl = lp[burn:].reshape(-1)
        weights = np.ones(len(samples))
        info.update(nwalkers=nwalkers, nsteps=nsteps, burnin_steps=burn, n_samples=int(len(samples)),
                    acceptance=float(np.mean(sampler.acceptance_fraction)))
        try:
            info["autocorr_time"] = sampler.get_autocorr_time(discard=burn, quiet=True).tolist()
        except Exception as exc:  # emcee raises when the chain is short compared to tau
            info["autocorr_time"] = str(exc)
        # Also the summaries without burn-in, as for the released chains
        all_samples = chain.reshape(-1, ndim)
        info["no_burnin"] = {n: weighted_stats(all_samples[:, k], np.ones(len(all_samples))) for k, n in enumerate(names)}
        info["no_burnin"]["Om"]["note"] = "all steps kept"
    else:
        raise ValueError(sampler_name)

    info["ncall_loglike"] = ncall[0]
    info["seconds"] = time.time() - t0
    np.savez_compressed(os.path.join(OUT, run + ".npz"), samples=samples, weights=weights, logl=logl, names=names)
    stats = {n: weighted_stats(samples[:, k], weights) for k, n in enumerate(names)}
    om = samples[:, names.index("Om")]
    ok = samples[:, names.index("Ok")] if "Ok" in names else 0.0
    stats["OL"] = weighted_stats(1.0 - om - ok, weights)
    if "h0" in names:
        stats["H0"] = weighted_stats(100.0 * samples[:, names.index("h0")], weights)
    info["stats"] = stats
    info["best_fit_chi2"] = float(-2.0 * np.max(logl))
    with open(out_json + ".part", "w") as f:
        json.dump(info, f, indent=1)
    os.replace(out_json + ".part", out_json)
    print(run, "done in %.0f s" % info["seconds"], "Om %.4f +- %.4f" % (stats["Om"]["mean"], stats["Om"]["std"]))


if __name__ == "__main__":
    for r in sys.argv[1:]:
        main(r)
