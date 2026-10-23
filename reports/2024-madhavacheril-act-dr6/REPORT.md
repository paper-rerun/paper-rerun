# Reproduction report: The Atacama Cosmology Telescope: DR6 Gravitational Lensing Map and Cosmological Parameters

- Paper: Madhavacheril, Qu, Sherwin, MacCrann, Li et al. (ACT Collaboration), ApJ 962:113, 2024. DOI: 10.3847/1538-4357/acff5f (arXiv:2304.05203). Lens-only S8^CMBL is quoted in the companion paper Qu et al., ApJ 962:112, 2024 (arXiv:2304.05202)
- Code: https://github.com/ACTCollaboration/act_dr6_lenslike @ 5d54308ec60acbf545fd4e46a10091cc6f8a2237
- Data: https://lambda.gsfc.nasa.gov/data/suborbital/ACT/ACT_dr6/likelihood/data/ACT_dr6_likelihood_v1.2.tgz (sha256 bbcde3bc...d3601085); BAO data from `cobaya-install` (bao_data); authors' public chains from https://portal.nersc.gov/project/act/act_dr6_lensing/chains/
- Target: (1) lensing-only S8^CMBL = σ8(Ωm/0.3)^0.25 (Qu+24, Sec. "Constraints on the amplitude of structure from lensing alone": 0.818 ± 0.022; also σ8Ωm^0.25 = 0.606 ± 0.016). (2) ACT lensing + BAO, Madhavacheril+24 Table 2: σ8 = 0.820 ± 0.015, S8 = 0.840 ± 0.028, Ωm = 0.315 ± 0.016, H0 = 68.2 ± 1.1 (abstract/eq.: σ8 = 0.819 ± 0.015, H0 = 68.3 ± 1.1)
- Verdict: Reproduced (both chains run to the paper's criterion, Gelman-Rubin R-1 < 0.01)
- Date: 2026-10-21 to 2026-10-22
- Hardware: Ryzen 9 3900X, 64 GB RAM, RTX 2070 SUPER 8 GB (unused), WSL2 Ubuntu 24.04; 10 threads (5 MPI chains × 2 OpenMP)

## Results

| Quantity | Paper | Ours | Diff |
|---|---|---|---|
| S8^CMBL, ACT lensing only | 0.818 ± 0.022 | 0.8165 ± 0.0215 | −0.0015 (0.07σ) |
| σ8 Ωm^0.25, ACT lensing only | 0.606 ± 0.016 | 0.6042 ± 0.0159 | −0.0018 (0.1σ) |
| σ8, ACT lensing + BAO | 0.820 ± 0.015 | 0.8192 ± 0.0146 | −0.0008 (0.05σ) |
| S8 = σ8(Ωm/0.3)^0.5, lensing + BAO | 0.840 ± 0.028 | 0.8401 ± 0.0281 | +0.0001 |
| Ωm, lensing + BAO | 0.315 ± 0.016 | 0.3157 ± 0.0161 | +0.0007 |
| H0, lensing + BAO | 68.2 ± 1.1 | 68.25 ± 1.11 | +0.05 |

Mean and 68% interval, first 30% of each chain removed as burn-in (env/summarize.py, output in logs/summary_lensonly_converged.txt and logs/summary_bao_converged.txt). Dropping 50% instead changes S8^CMBL by −0.0005 and leaves σ8 (BAO) unchanged.

Convergence. The paper (App. A) runs to Gelman-Rubin R-1 < 0.01. Both runs reached it and Cobaya stopped them itself ("The run has converged!", same stop rule as the authors' yaml: Rminus1_stop 0.01 and Rminus1_cl_stop 0.2):
- lens-only: R-1 = 0.0099, R-1 of the 95% bounds = 0.084, after 25250 accepted samples in 5 chains.
- lens + BAO: R-1 = 0.0075, R-1 of the bounds = 0.067, after 19365 accepted samples in 5 chains.

Both runs were stopped once at an intermediate point (lens-only at R-1 = 0.035, lens + BAO at R-1 = 0.057) and later continued with `cobaya-run --resume`, same yamls, same 5 MPI × 2 threads. At that intermediate point the results were already within 0.2σ of the paper (S8^CMBL = 0.8145 ± 0.0207, σ8 = 0.8192 ± 0.0142).

With the converged chains our lens-only S8^CMBL agrees with the authors' public chain to 0.0002.

Reference: the authors' own public chains, analysed with the same script, give S8^CMBL = 0.8163 ± 0.0219 (lens-only root `lcdm_act_baseline_nobao_167989490589`). For the BAO root `lcdm_act_baseline_rerun_167934952674` they give σ8 = 0.8198 ± 0.0147, S8 = 0.8398 ± 0.0282, Ωm = 0.3150 ± 0.0160, H0 = 68.25 ± 1.11, matching Table 2.

## What it took

1. Cloned the repo. The authors' public chain `.updated.yaml` files show what they ran: Cobaya 3.2.2, CAMB 1.3.6, priors equal to Madhavacheril+24 Table 1. Those are ombh2 ~ N(0.02233, 0.00036), ns ~ N(0.96, 0.02), logA in [1.61, 4], omch2 in [0.005, 0.99], 100θMC in [0.5, 10], H0 kept in [40, 100], Σmν = 0.06 eV with one massive neutrino, `lens_only: true`, `variant: act_baseline`. For BAO: 6dF, SDSS DR7 MGS, BOSS DR12 LRG and eBOSS DR16 LRG.
2. Our run yamls (env/lensonly.yaml, env/lensbao.yaml) are the authors' input yamls with only these changes (patches/*.diff): output path, packages path, and the proposal covmat set to the authors' published `.covmat`. The covmat affects only how fast the sampler mixes, not the posterior.
3. Environment problems, all fixed without touching the authors' code:
   - Latest stack (Cobaya 3.6.2 + CAMB 2.0.5): all 11 Cobaya tests fail with `CAMBUnknownArgumentError: Unrecognized parameter: lens_margin`. The README and the paper's accuracy settings use `lens_margin`, which CAMB 2.x removed. Fix: pin CAMB 1.3.6 and Cobaya 3.2.2 with numpy<2 and scipy<1.12. CAMB 1.3.6 needs `setuptools<70` (it imports pkg_resources) and `--no-build-isolation`. Lockfile: env/requirements-pinned.lock.txt.
   - Cobaya 3.6.2 also raises `ComponentNotInstalledError` unless the data sit in a Cobaya packages path, because `is_installed(path=None)` fails. We unpacked the tarball to packages/data/ACT_dr6_likelihood/v1.2. Cobaya 3.2.2 loads the in-repo data/ copy without this.
   - Cobaya 3.2.2 + pandas 3.0.6: BAO likelihoods crash on `assert self.has_type`, because string columns are no longer dtype object. The BAO MCMC and post-processing used a second venv with pandas 2.0.3 (env/requirements-post.lock.txt). The lens-only MCMC ran on pandas 3.0.6. Its chain weights were checked and are correct (repeated points get weight > 1).
   - The LAMBDA download ran at ~200 KB/s (~30 min). With aria2c and 16 connections it took 2 min.
4. Sanity check: on the pinned stack the repo tests `test_act_baseline_lensonly` and `test_act_baseline` pass (χ² = 14.00).
5. Runtime (the two runs went one after the other, never more than 10 threads): lens-only MCMC 7h39m of sampling (2h10m plus 5h29m after resume), lens + BAO MCMC 7h12m (1h45m plus 5h27m). That's about 1.7–3.3 s per step per chain at 2 threads, with other jobs sharing the CPU. The session took about 16 h of wall-clock time in total, from setup to the final summary.
6. Extra check, done on the intermediate lens-only chain: importance-reweighting it with the four BAO likelihoods (env/post_bao.yaml, output in logs/post_bao_reweight/) gives σ8 = 0.821 ± 0.015. With an effective sample size of only ~17 it is a qualitative check only.
7. Extra check: Qu+24's prior table differs from Madhavacheril+24 Table 1 (logA in [2,4], ombh2 ~ N(0.0223, 0.0005)). Reweighting both our intermediate chain and the authors' public chain to the Qu+24 priors moves S8^CMBL by less than 0.0005. So the prior difference does not explain the 0.816 (public chain) vs 0.818 (Qu+24 text) gap. That gap is only 0.1σ.

Files: env/setup.sh (full recipe), env/run_chain.sh, env/summarize.py, env/reweight_qu23_priors.py, logs/chains_lensonly/, logs/chains_bao/, logs/summary_*.txt (the *_converged.txt files hold the final numbers), logs/run_*.part1.log plus logs/run_*.log for the resumed runs, logs/pytest*.log.

## Notes for the authors

Friendly issue draft (not posted):

> Thanks for releasing the likelihood, data and chains, they made this reproduction easy. A few things we hit in Oct 2026:
> 1. With current CAMB (2.0.x) every Cobaya run with the recommended settings fails: `lens_margin` is no longer a CAMB argument. That covers the README "Recommended theory accuracy", ACTDR6LensLike-example.yaml and tests/test_cobaya.py. Pinning camb==1.3.6 works (it needs setuptools<70 to build). It would help to say which CAMB versions are supported, or to drop or replace `lens_margin` for CAMB ≥ 2.
> 2. With Cobaya 3.6, `ACTDR6LensLike` raises ComponentNotInstalledError unless a packages_path holds the data, even when the data are in act_dr6_lenslike/data/. This may be the same as #19/#27.
> 3. The lens-only S8^CMBL in Qu+24 (0.818 ± 0.022) differs slightly from the public chain lcdm_act_baseline_nobao_167989490589 (0.816 ± 0.022). Also, the prior table in Qu+24 (logA in [2,4], Ωbh² ~ N(0.0223, 0.0005)) differs from the priors in that chain and in Madhavacheril+24 Table 1. Reweighting shows the prior difference doesn't matter (<0.0005), but naming the chain behind each quoted number would help.
> 4. Minor: Madhavacheril+24 quotes σ8 = 0.819 ± 0.015 and H0 = 68.3 ± 1.1 in the abstract and equation, but 0.820 ± 0.015 and 68.2 ± 1.1 in Table 2. The public chain gives 0.8198 and 68.25.

## Independent reproductions

No ReScience C or other independent reproduction found (web search, Oct 2026). The repo's GitHub issues (#1–#29) are about installation and packaging, not results.

## How this report was made

This reproduction was run by AI agents (Claude, by Anthropic) on a home computer and reviewed by a human before publication. No number in this report was estimated or typed by hand: each one comes from code that ran on this machine, and the commands, logs and outputs are in this folder.

A single agent read the paper, built the environment, ran the authors' code and released data on a Ryzen 9 3900X (CPU only), compared the results with the paper and wrote this report. A coordinating agent checked the report against the logs, and a human approved publication. This was a pilot run, before we added blind recomputation by a second agent.

We do this because most published code is never re-run by anyone else, and AI agents make that check cheap. The method, prompts and scripts are public at https://github.com/paper-rerun/paper-rerun/blob/main/METHOD.md, so anyone can run the same checks on papers in their own field.

Contact: Filipe Tessaro, https://github.com/paper-rerun/paper-rerun/issues
